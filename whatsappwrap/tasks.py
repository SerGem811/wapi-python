import json
import threading
from datetime import datetime
from time import sleep

import requests
from rest_framework.authtoken.models import Token
from webwhatsapi import WhatsAPIDriverStatus

from whatsappwrap.celery import app
from whatsappwrap.models import Instance, WebhookUrl
from whatsappwrap.utils import init_driver

timers = dict()
semaphores = dict()
drivers = dict()

@app.task(bind=True)
def get_instances(self):
    return list(Instance.objects.values_list('token', flat=True))


@app.task(bind=True)
def get_webhook(self):
    obj = WebhookUrl.objects.first()
    if obj:
        return getattr(obj, "url")
    else:
        return "http://google.com/"


@app.task(bind=True)
def init_client(self, client_id):
    """Initialse a driver for client and store for future reference

    @param client_id: ID of client user
    @return whebwhatsapi object
    """

    if client_id not in get_instances():
        token = Token.objects.get(key=client_id)
        drivers[client_id] = init_driver(client_id)
        try:
            instance = Instance.objects.create(token=token, is_loggedin=False, autoconnect=True)
            instance.save()
        except Exception as exc:
            print(exc)
        #app.send_task(name="wait_messages", args=(client_id,))
        wait_messages(client_id)
        # drivers[client_id].subscribe_new_messages(NewMessageObserver())
    elif client_id not in drivers:
        drivers[client_id] = init_driver(client_id)
        wait_messages(client_id)
    return drivers[client_id]


def wait_messages(client_id):
    try:
        print("Started observer", client_id)
        sleep(10)
        drivers[client_id].subscribe_new_messages(NewMessageObserver())
        while True:
            sleep(5)
    except Exception as exc:
        print("Error", exc)
        wait_messages(client_id)


class NewMessageObserver:
    def on_message_received(self, new_messages):
        for message in new_messages:
            if message.type == 'chat':
                print("New message '{}' received from number {}".format(message.content, message.sender.id))
                save_messagereceived_webhook(message)
            else:
                print("New message of type '{}' received from number {}".format(message.type, message.sender.id))


def save_messagereceived_webhook(message):
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    try:
        data = {
            "messages": [
                {
                    "id": message.id,
                    "body": message.content,
                    "senderName": message.sender.get_safe_name(),
                    "fromMe": False,
                    "author": message.sender.id,
                    "time": str(int(datetime.timestamp(message.timestamp))),
                    "chatId": message.chat_id["_serialized"],
                    "messageNumber": 1,
                    "to": message.to["_serialized"],
                    "type": "chat"
                }
            ]
        }
        print(data)
        r = requests.post(get_webhook(), json=data, headers=headers)
        print(r.status_code, r.text)
    except Exception as exc:
        print(exc)


@app.task(bind=True)
def get_messages(self, client_id, chat_id, mark_seen):
    """Return all of the chat messages"""
    driver = drivers.get(client_id)
    chat = driver.get_chat_from_id(chat_id)
    msgs = list(driver.get_all_messages_in_chat(chat, include_me=True))

    if mark_seen:
        for msg in msgs:
            try:
                msg.chat.send_seen()
            except:
                pass

    return msgs


@app.task(bind=True)
def get_client_info(client_id):
    """Get the status of a perticular client, as to it is connected or not

    @param client_id: ID of client user
    @return JSON object {
        "driver_status": webdriver status
        "is_alive": if driver is active or not
        "is_logged_in": if user is logged in or not
        "is_timer": if timer is running or not
    }
    """
    if client_id not in drivers:
        return None

    driver_status = drivers[client_id].get_status()
    is_alive = False
    is_logged_in = False
    if (driver_status == WhatsAPIDriverStatus.NotLoggedIn
            or driver_status == WhatsAPIDriverStatus.LoggedIn):
        is_alive = True
    if driver_status == WhatsAPIDriverStatus.LoggedIn:
        is_logged_in = True

    return {
        "is_alive": is_alive,
        "is_logged_in": is_logged_in,
        "is_timer": bool(timers[client_id]) and timers[client_id].is_running
    }


@app.task(bind=True)
def check_new_messages(client_id):
    """Check for new unread messages and send them to the custom api
    @param client_id: ID of client user
    """
    # Return if driver is not defined or if whatsapp is not logged in.
    # Stop the timer as well
    if client_id not in drivers or not drivers[client_id] or not drivers[client_id].is_logged_in():
        timers[client_id].stop()
        return

    # Acquire a lock on thread
    if not acquire_semaphore(client_id, True):
        return

    try:
        # Get all unread messages
        res = drivers[client_id].get_unread()
        # Mark all of them as seen
        for message_group in res:
            message_group.chat.send_seen()
        # Release thread lock
        release_semaphore(client_id)
        # If we have new messages, do something with it
        if res:
            print(res)
    except:
        pass
    finally:
        # Release lock anyway, safekeeping
        release_semaphore(client_id)


def acquire_semaphore(client_id, cancel_if_locked=False):
    if not client_id:
        return False

    if client_id not in semaphores:
        semaphores[client_id] = threading.Semaphore()

    timeout = 10
    if cancel_if_locked:
        timeout = 0

    val = semaphores[client_id].acquire(blocking=True, timeout=timeout)

    return val


def release_semaphore(client_id):
    if not client_id:
        return False

    if client_id in semaphores:
        semaphores[client_id].release()

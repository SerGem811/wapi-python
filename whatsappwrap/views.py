import json
from datetime import datetime
from json import JSONEncoder
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.template import loader
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from whatsappwrap.models import Instance
from whatsappwrap.serializers import TokenSerializer, SendMessageSerializer, ReadMessageSerializer, \
    AutoconnectSerializer, RegisterSerializer
from whatsappwrap.tasks import init_client, drivers, get_messages



class AutoconnectView(GenericAPIView):
    serializer_class = AutoconnectSerializer

    def post(self, request):
        if request.data.get("token") is None:
            raise NotAuthenticated
        try:
            serializer = AutoconnectSerializer(data=request.data)
            if serializer.is_valid():
                if request.data.get("set"):
                    instance = Instance.objects.get(token=request.data.get("token"))
                    instance.autoconnect = request.data.get("set")
                    instance.save()
                    return Response({"succcess": True})
                else:
                    instance = Instance.objects.get(token=request.data.get("token"))
                    return Response({"autoconnect": instance.autoconnect})
            else:
                return Response({"succcess": False})
        except ObjectDoesNotExist:
            raise AuthenticationFailed
        except Exception as exc:
            print(exc)
            content = {'success': False}
            return Response(content)


class GetQRView(GenericAPIView):
    serializer_class = TokenSerializer

    def post(self, request):
        if request.data['token'] is None:
            raise NotAuthenticated
        try:
            driver = init_client(request.data['token'])
            qrbase64 = driver.get_qr_base64()
            content = {'qr': qrbase64}
            # driver.save_firefox_profile()
            return Response(content)
        except ObjectDoesNotExist:
            raise AuthenticationFailed
        except Exception as exc:
            print(exc)
            content = {'qr': None}
            return Response(content)


class StatusView(GenericAPIView):
    serializer_class = TokenSerializer

    def post(self, request):
        if request.data['token'] is None:
            raise NotAuthenticated
        try:
            serializer = TokenSerializer(data=request.data)
            serializer.is_valid()
            data = serializer.validated_data
            driver = drivers[data['token']]
            status = driver.is_logged_in()
            if status:
                content = {'accountStatus': 'authenticated'}
            else:
                content = {'accountStatus': 'init'}
            internet = driver.is_connected()
            if internet:
                content.update({'internetStatus': 'connected'})
            else:
                content.update({'internetStatus': 'disconnected'})
            return Response(content)
        except ObjectDoesNotExist:
            raise AuthenticationFailed
        except Exception as exc:
            print(exc)
            content = {'accountStatus': 'init', 'internetStatus': 'disconnected'}
            return Response(content)


class MyContactsView(GenericAPIView):
    serializer_class = TokenSerializer

    def post(self, request):
        if request.data['token'] is None:
            raise NotAuthenticated
        try:
            serializer = TokenSerializer(data=request.data)
            serializer.is_valid()
            data = serializer.validated_data
            driver = drivers[data['token']]
            contacts = driver.get_my_contacts()
            result = []
            for contact in contacts:
                result.append({'id': contact.id,
                               'shortName': contact.short_name,
                               'pushname': contact.push_name,
                               'formattedName': contact.push_name,
                               'profilePic': contact.profile_pic,
                               })
            content = {'contacts': result}
            return Response(content)
        except ObjectDoesNotExist:
            raise AuthenticationFailed
        except Exception as exc:
            print(exc)
            content = {'status': 'fail'}
            return Response(content)


class GetContactsView(GenericAPIView):
    serializer_class = TokenSerializer

    def post(self, request):
        if request.data['token'] is None:
            raise NotAuthenticated
        try:
            serializer = TokenSerializer(data=request.data)
            serializer.is_valid()
            data = serializer.validated_data
            driver = drivers[data['token']]
            contacts = driver.get_contacts()
            result = []
            for contact in contacts:
                result.append({'id': contact.id,
                               'shortName': contact.short_name,
                               'pushname': contact.push_name,
                               'formattedName': contact.push_name,
                               'profilePic': contact.profile_pic,
                               })
            content = {'contacts': result}
            return Response(content)
        except ObjectDoesNotExist:
            raise AuthenticationFailed
        except Exception as exc:
            print(exc)
            content = {'status': 'fail'}
            return Response(content)


class GetChatsView(GenericAPIView):
    serializer_class = TokenSerializer

    def post(self, request):
        if request.data['token'] is None:
            raise NotAuthenticated
        try:
            serializer = TokenSerializer(data=request.data)
            serializer.is_valid()
            data = serializer.validated_data
            driver = drivers[data['token']]
            chats = driver.get_all_chats()
            print(chats)
            result = []
            for chat in chats:
                result.append({'id': chat.id,
                               'name': chat.short_name})
            content = {'chats': result}
            return Response(content)
        except ObjectDoesNotExist:
            raise AuthenticationFailed
        except Exception as exc:
            print(exc)
            content = {'status': 'fail'}
            return Response(content)


class SendMessageView(GenericAPIView):
    serializer_class = SendMessageSerializer

    def post(self, request):
        if request.data['token'] is None:
            raise NotAuthenticated
        if drivers.get(request.data['token']) is not None:
            serializer = SendMessageSerializer(data=request.data)
            serializer.is_valid()
            data = serializer.validated_data
            driver = drivers[data['token']]
            chatobj = driver.get_chat_from_phone_number(data['phone'], createIfNotFound=True)
            driver.send_message_to_id(chatobj.id, data['message'])
            content = {'message': data['message'], 'phone': data['phone'],
                       'timestamp': datetime.timestamp(datetime.now())}
        else:
            content = {'status': 'whatsapp_not_authenticated'}

        return Response(content)


class ReadMessageView(GenericAPIView):
    serializer_class = ReadMessageSerializer

    def post(self, request):
        if request.data['token'] is None:
            raise NotAuthenticated
        if drivers.get(request.data['token']) is not None:
            serializer = ReadMessageSerializer(data=request.data)
            serializer.is_valid()
            data = serializer.validated_data
            driver = drivers[data['token']]
            chat_id = driver.get_chat_from_phone_number(data['phone']).id
            mark_seen = True
            messages = get_messages(data['token'], chat_id, mark_seen)
        else:
            content = {'status': 'whatsapp_not_authenticated'}
            return Response(content)
        result = []
        for message in messages:
            result.append({"sender": message.sender.get_safe_name(),
                           "message": message.content,
                           "timestamp": message.timestamp})
        content = {'messages': result}
        return Response(content)


def qrview(request):
    template = loader.get_template('pages/qr.html')
    return HttpResponse(template.render({}, request))

class RetrieveTokenView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                obj = User.objects.get(username=request.data.get("username"))
                if not obj.check_password(request.data.get("password")):
                    raise NotAuthenticated
                token = Token.objects.get(user=obj).key
                return Response({"token": token})
            except ObjectDoesNotExist:
                obj = User.objects.create(username=request.data.get("username"), password=request.data.get("password"))
                obj.save()
                token = Token.objects.get(user=obj).key
                return Response({"token": token})
            except Exception as exc:
                print(exc)
                return Response({"status": "fail"})

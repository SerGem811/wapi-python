# Installation Guide

Project was developed in a Linux Environment to run in Linux Environment (Preferably Ubuntu 18.04+)

Install Firefox and Geckodriver

```bash
wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz && tar xvf geckodriver-v0.26.0-linux64.tar.gz
```

```bash
sudo cp geckodriver /usr/bin/
```



```bash
wget https://download-installer.cdn.mozilla.net/pub/firefox/releases/61.0.2/linux-x86_64/en-US/firefox-61.0.2.tar.bz2 && bunzip2 firefox-61.0.2.tar.bz2 &&tar xvf firefox-61.0.2.tar
```

```bash
sudo ln -s ./firefox/firefox /usr/local/bin/firefox
```

Assuming that you transferred the project files, have Python3.6+ and pip installed.

```bash
pip install -r requirements.txt
```

Make migrations & migrate for DB

```bash
python3 manage.py makemigrations && python3 manage.py makemigrations whatsappwrap
```

```bash
python3 manage.py migrate
```

Start the project with (preferably inside a "screen" session)

```bash
python3 manage.py runserver (optional IP:PORT)
```

or 

```bash
python manage.py runserver (optional IP:PORT)
```

# Endpoints

## *POST* /qr/

Receives token, returns QR scan image as base64 format.

If it fails, or waiting for sessions to start, it returns **null**.

## *POST* /sendmessage/

Receives token, phone, message.

Phone must be in 5521980008000 format.

Returns status. See the REST test page for detailed view.

## *POST* /readmessage/

Receives token, phone.

Returns latest conversation from specified phone.

## *POST* /status/

Receives token.

Returns current status. See test page for details.

## *POST* /getmycontacts/

Receives token.

Returns current contacts.

## *POST* /getcontacts/

Receives token.

Returns contacts.

## *POST* /getchats/

Receives token.

Returns all chats.

## *POST* /autoconnect/

Receives token and set (value 0 or 1, optional).

Returns the autoconnect status if set value is empty.

# Modifications to the library

Webwhatsapi - \__init\__.py

Add specified block to the 262. line after the self.driver.refresh()

This makes the sessions **autoconnect** on another session start.

```python
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, self._SELECTORS['qrCode']))
        WebDriverWait(self.driver, 50).until(element_present)
        script = '''var attachEl=function(){waitForEl(".overlay",function(){$.ajax({type:"POST",url:"'''+ self.server_ip +'''",data:{token:"'''+ self.username +'''"},dataType:"json"}).done(function(t){if(1==t.autoconnect){var e=document.evaluate("//div[@role='button']",document.body,null,XPathResult.ANY_TYPE,null);e.iterateNext(),e.iterateNext().click()}else console.log(t)}),setTimeout(function(){attachEl()},2e3)})},waitForEl=function(t,e){jQuery(t).length?e():setTimeout(function(){waitForEl(t,e)},2e3)};!function(){(new Date).getTime();var t=document.createElement("SCRIPT");t.src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js",t.type="text/javascript",t.onload=function(){window.jQuery,attachEl()},document.getElementsByTagName("head")[0].appendChild(t)}();'''
        self.driver.execute_script(script)
    except:
        pass
```
Should look like this

![image](https://i.hizliresim.com/1p8Vz5.png)

On line 196 add these, replace the server_ip with your autoconnect url in the same format

```python
self._profile.DEFAULT_PREFERENCES['frozen']["security.mixed_content.block_active_content"] = False
self.server_ip = "http://192.168.1.1:8000/autoconnect/"
```

Also, replace the line 72, qrCode variable value with 

```python
'qrCode': "canvas[aria-label=\"Scan me!\"]",
```

Webwhatsapi - objects/message.py

Line 61, right after self.chat_id...

```python
self.to = js_obj['to']
```

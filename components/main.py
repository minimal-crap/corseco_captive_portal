import os
import json
import time
import datetime
import random
import subprocess
import socket
import base64


from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler
from tornado.web import Application
from tornado.web import StaticFileHandler
from twilio.rest import TwilioRestClient
import requests as rq

import db_handler

secret_key_db_handler_instance = db_handler.DBHandler()
otp_db_handler_instance = db_handler.DBHandler(table_name="client_otp", column_name="otp")

active_clients = list()
host = "192.168.42.1"
port = 8000
GOOGLE_API_KEY = "AIzaSyDwa6GFZkseZqQ_Vv2yvSLBA_nfHVtCgKw"
GOOGLE_CLOUD_VISION_URL = "https://vision.googleapis.com/v1/images:annotate"


def get_image_features(file_path):
    try:
        with open(file_path, 'rb') as image_handle:
            b64_string = base64.b64encode(image_handle.read())

        req_data = {
            "requests": [
                {
                    "image": {
                        "content": b64_string
                    },
                    "features": [
                        {
                            "type": "LABEL_DETECTION",
                            "type": "TEXT_DETECTION",
                            "maxResults": 1
                        }
                    ]
                }
            ]
        }

        r = rq.post("{}?key={}".format(
            GOOGLE_CLOUD_VISION_URL,
            GOOGLE_API_KEY),
            json.dumps(req_data),
            headers={'content-type': 'application/json'})
        return json.loads(r.text)
    except Exception as err:
        print(err.message)


def whitelist_ip(ip_address):
    """Method to whitelist ip address."""
    try:
        if socket.inet_aton(ip_address):
            timestamp = time.mktime(
                datetime.datetime.now().timetuple()
            )
            if otp_db_handler_instance.whitelist_entry_db(ip_address, timestamp):
                command = "sudo iptables -t nat -D PREROUTING -p tcp -s {} --dport 80 -j DNAT --to-destination {}:{}".format(
                    ip_address, host, port)
                subprocess.call(command.split())
                command2 = "sudo ipset del blacklist {}".format(ip_address)
                subprocess.call(command2.split())
    except Exception as err:
        print(err)


def blacklist_ip(ip_address):
    """Method to blacklist ip address."""
    try:
        if socket.inet_aton(ip_address):
            command = "sudo iptables -t nat -A PREROUTING -p tcp -s {} --dport 80 -j DNAT --to-destination {}:{}".format(
                ip_address, host, port)
            subprocess.call(command.split())
            command2 = "sudo ipset add blacklist {}".format(ip_address)
            subprocess.call(command2.split())
    except Exception as err:
        print(err)



class ImageAPIHandler(RequestHandler):
    """ImageAPIHandler class to handle image api process requests"""
    
    def post(self, *args, **kwargs):
        """Post method for ImageAPIHandler class."""



class ClientIPHandler(RequestHandler):
    """ClientIPHandler class to handle ip process request."""

    def post(self, *args, **kwargs):
        """Post method for ClientIPHandler class."""

        received_otp = self.request.body.split("=")[1]
        current_otp = otp_db_handler_instance.get_client_data()
        if current_otp == received_otp:
            whitelist_ip(self.request.remote_ip)
            otp_db_handler_instance.delete_client_data()
            secret_key_db_handler_instance.delete_client_data()
            self.redirect("http://{}:{}/success/".format(host, port))
        else:
            self.redirect("http://{}:{}/error/".format(host, port))


def send_input_hook_to_client(client):
    try:
        client_key = client.request.headers.get("Sec-Websocket-Key")
        current_key = secret_key_db_handler_instance.get_client_data()

        if current_key is None:
            return False
        if client_key == current_key:
            message = dict()
            message["number_input_hook"] = "true"
            client.write_message(json.dumps(message))
            return True
        else:
            return False
    except Exception as err:
        print("send_input_hook_to_client: {}".format(err.message))


def send_to_clients(message):
    print("active clients: {}".format(len(active_clients)))
    for client in active_clients:
        try:
            current_key = client.request.headers.get("Sec-Websocket-Key")
            client_key = secret_key_db_handler_instance.get_client_data()
            if current_key == client_key:
                client.write_message(message)

        except Exception as err:
            print("websocket err: {}".format(err.message))
            active_clients.remove(client)


class PortalIndex(RequestHandler):
    def get(self):
        self.render("./templates/home.html")


class TermsPageHandler(RequestHandler):
    def get(self):
        self.render("./templates/terms.html")


class OTPSucessHandler(RequestHandler):
    def get(self):
        self.render("./templates/success.html")


class OTPMismatchHandler(RequestHandler):
    def get(self):
        self.render("./templates/error.html")


class SMSHandler(RequestHandler):
    """SMSHandler class for sms endpoint."""

    def set_default_headers(self):
        print "setting headers!!!"
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "X-Requested-With, XMLHttpRequest")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS, TEXT")

    def post(self, *args, **kwargs):
        data = self.request.body
        data = json.loads(data)
        if "number" in data:
            try:
                client_otp = otp_db_handler_instance.get_client_data()
                if client_otp is not None:
                    otp_db_handler_instance.delete_client_data()
                current_otp = random.randint(10000, 99999)
                otp_db_handler_instance.set_client_data(str(current_otp))

                account_sid = "AC5ad8bd2722f2b48884947312e7a353ef"
                account_token = "fc973cb6503f2298177c8cc21015dede"
                from_a = "+12162202703"
                destination_number = data["number"]

                client = TwilioRestClient(account_sid, account_token)

                message = client.messages.create(
                    body="Your OTP for 7UP Wi-Fi is {}".format(str(current_otp)),
                    to=destination_number,
                    from_=from_a,
                )
            except Exception as err:
                print("SMSHandler::post: {}".format(err.message))

    get = post

    # def options(self):
    #     self.set_status(204)
    #     self.finish()


class ClientSocketHandler(WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("client internet request received!")
        if self not in active_clients:
            print(self.request.headers.get("Sec-Websocket-Key"))
            active_clients.append(self)
            message = dict()
            if secret_key_db_handler_instance.get_client_data() is None:
                secret_key_db_handler_instance.set_client_data(
                    self.request.headers.get("Sec-Websocket-Key"))
                message["success"] = "please scan the 7up bar code at counter"
                send_to_clients(json.dumps(message))
            else:
                message["error"] = "You are in queue, sorry for inconvenience."
                self.write_message(json.dumps(message))

    def on_message(self, message):
        self.write_message(json.loads(message))
        print(self.request.headers.get("Sec-Websocket-Key"))
        print(message)

    def on_close(self):
        print("client connection closed!")

        current_key = str(self.request.headers.get("Sec-Websocket-Key"))
        client_key = secret_key_db_handler_instance.get_client_data()

        if client_key is not None and client_key == current_key:
            secret_key_db_handler_instance.delete_client_data()

        if self in active_clients:
            active_clients.remove(self)


class ClientPushHandler(RequestHandler):
    def post(self, *args, **kwargs):
        data = self.request.body
        send_to_clients(data)


class ClientNumberInputHookHandler(RequestHandler):
    def get(self):
        client_secret_key = secret_key_db_handler_instance.get_client_data()
        for client in active_clients:
            current_secret_key = client.request.headers.get("Sec-Websocket-Key")
            if current_secret_key == client_secret_key:
                send_input_hook_to_client(client)


class MainApplication(Application):
    def __init__(self):
        handlers = [
            (r"/portal", PortalIndex),
            (r"/", TermsPageHandler),
            (r"/push_data_to_clients/", ClientPushHandler),
            (r"/client_push_server/", ClientSocketHandler),
            (r"/client_input_hook_push_server/", ClientNumberInputHookHandler),
            (r"/send_sms/", SMSHandler),
            (r"/allow_internet/", ClientIPHandler),
            (r"/success/", OTPSucessHandler),
            (r"/error/", OTPMismatchHandler),
            (r"/static/(.*)", StaticFileHandler,
             {"path": "/home/sud/minimalcrap/corseco_captive_portal/components/templates/assets/"})
        ]
        Application.__init__(self, handlers)


def main():
    app_instance = MainApplication()
    secret_key_db_handler_instance.delete_client_data()
    blacklist_command = "sudo sh /home/pi/initiate_blacklist.sh"
    # subprocess.call(blacklist_command.split())
    otp_db_handler_instance.delete_client_data()
    print("[*]starting app at {}".format(port))
    app_instance.listen(port, address=host)
    IOLoop.instance().start()


if __name__ == "__main__":
    main()

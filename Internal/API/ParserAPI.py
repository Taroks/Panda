import requests
from config import *
from flask import Flask, Response
from Internal.PARSER.Parser import ParseToXml, ParseToJson
from External.FTP.ftp_client import *
from threading import Thread
from requests.exceptions import ReadTimeout, ConnectionError
from requests.exceptions import ConnectionError, ReadTimeout
import subprocess
import os
import time
from requests_kerberos import HTTPKerberosAuth

app = Flask(__name__)

def start_ws_server(command):
    try:
        print("subprosses is in a way")
        process = subprocess.Popen(command, shell=True, cwd="/var/www/panda-back/Internal/WS_SERVER/")
        process.poll()
        print(process.returncode)
        #print(process.stderr.read().decode("utf-8"))
    except subprocess.CalledProcessError as e:
        print("subprocess error is -- {}".format(e))

@app.route('/')
def foo():
    return Response('OK', status=200)

@app.route("/ParserAPI/GetFile/", methods=['GET'])
def download_xml():
    # Получение xml файла для парсинга
    # try:
    downloader()
    return 'OK', 200
    # except:
        # return '', 500


@app.route("/ParserAPI/ParseFile/", methods=['GET'])
def parse_xml():
    # Парсинг xml файла в json
    # try:
    ParseToJson().get_element_tree()
    return 'OK', 200
    # except:
    #     return '', 500


@app.route("/ParserAPI/MakeXML/", methods=['GET'])
def make_xml():
    ParseToXml().make_xml()
    return 'ok'


@app.route("/ParserAPI/SendData/", methods=['GET'])
def send_requests():
    s = time.time()
    command = "python3 server.py &"
    start_ws_server(command)
    for _ in SERVICES_LINKS:
        try:
            requests.post(_, timeout=1, auth=HTTPKerberosAuth(delegate=True))
            print("{} was sent????".format(_))
        except ReadTimeout as t:
            print("Requst was sent, waiting for data")
            continue
        except ConnectionError as c:
            print("service {} is unvailable. can't send data, trying next one".format(_))
            continue
        except Exception as e:
            exc = "error from service:" + str(e)
            print(exc)
            print(type(e))
        continue
    t = time.time() - s
    return "Data was sent by " + str(t) + "sec"

#опрос всех сервисов.
@app.route("/ParserAPI/GetData/", methods=["GET"])
def get_everything():
    flag = False
    if not os.path.exists(os.path.abspath(os.path.join(BASE_DIR, INTERNAL_DIR, DATA_DIR, SERVICES_DATA_DIR, FILES_FROM_SERVICES))):
        with open(os.path.abspath(os.path.join(BASE_DIR, INTERNAL_DIR, DATA_DIR, SERVICES_DATA_DIR, FILES_FROM_SERVICES)), "w", encoding="UTF-8") as k:
            pass
    else:
        if os.path.getsize(os.path.abspath(os.path.join(BASE_DIR, INTERNAL_DIR, DATA_DIR, SERVICES_DATA_DIR, FILES_FROM_SERVICES))) != 0:
            with open(os.path.abspath(
                    os.path.join(BASE_DIR, INTERNAL_DIR, DATA_DIR, SERVICES_DATA_DIR, FILES_FROM_SERVICES)), "w",
                      encoding="UTF-8") as k:
                pass
    # th = Thread(target=start_ws_server)
    # th.start()
    for _ in SERVICES_LINKS:
        try:
            s = requests.get(_, timeout=1)
        except ConnectionError:
            print("Сервис {} выключен или недоступен".format(_))
        except ReadTimeout:
            print("Ответ от сервиса {} на запрос не получен, однако это не повлияло на передачу данных".format(_))
        except Exception as e:
            print(type(e))
    return "kk"

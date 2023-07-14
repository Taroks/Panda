import asyncio
import websockets
import json
import time
# import gssapi
import ssl
# from gssapi.exceptions import GSSError
import os
from config import *
from websockets.exceptions import ConnectionClosed
import logging
import sys



class WS_Server():
    # #Определить url и headers сервера

    #
    # url = "wss://192.168.14.2:8765/socket"
    # headers = {"Authorization":"Negotiate"}
    #
    # #Определить принципал кербероса и файл с расширением .keytab
    # principal = "smozi-server2.ksue.rk@KSUE.RK"
    # keytab_file = "etc/krb5.keytab"
    #
    # #Создать контекст кербероса используя gssapi
    # # creds = gssapi.Credentials.from_keytab(principal, keytab_file)
    # # context = gssapi.SecurityContextt(creds=creds, usage="accept")

    def __init__(self):
        logging.basicConfig(level=logging.INFO, filename="/var/tmp/pandas_ws_server.log", filemode="a", format="%(asctime)s, %(levelname)s, %(message)s")
        #loop = asyncio.get_event_loop()
        with open(os.path.abspath(os.path.join("/var/www/panda-back/", INTERNAL_DIR, DATA_DIR, SERVICES_DATA_DIR, PARSED_DATA_NAME)), 'r', encoding="utf-8") as parsed_data:
            self.data_dict = json.load(parsed_data)
            logging.info("файл с выгрузкой открыт")
        self.i = 0 #счетчик соединений

    async def handler(self, websocket, path):
        try:
            # Отправка сообщения
            # message = {"message": "Hello, world!"}
            # await websocket.send(json.dumps(message))

            # Получение сообщения
            while True:
                a = time.time()
                message = await websocket.recv()
                data = json.loads(message)
                if len(data.keys()) == 1:
                    for i in data.get("table_names", "-"):
                        if not i == "-":
                            dicts = self.data_dict.get(i, "")
                            tables = {i: dicts}
                            await websocket.send(json.dumps(tables, ensure_ascii=False))
                            logging.info(str(i) + " -- отправлено")
                        else:
                            await websocket.send(json.dumps("неверно введен ключ сообщения на стороне клиента", ensure_ascii=False))
                    b = time.time()-a
                    logging.info("Общее время отправки всех таблиц клиентам для сервера составило: " + str(b))
                    break
                else:
                    with open(
                            os.path.abspath(
                                os.path.join('/var/www/panda-back/', INTERNAL_DIR, DATA_DIR, SERVICES_DATA_DIR, FILES_FROM_SERVICES)),
                            "a", encoding="UTF-8") as file_for_parsed_data:
                        json.dump(data, file_for_parsed_data, indent=4, ensure_ascii=False)
        except websockets.exceptions.ConnectionClosed:
            logging.error("Сокет-клиент {} закрыл соединение".format(websocket.remote_address))
            self.i += 1
            if i == len(SERVICES_LINKS):
                sys.exit(0)
        except asyncio.exceptions.CancelledError:
            await websocket.send(json.dumps("Ошибка преджевременного выхода из event loop", ensure_ascii=False))
            logging.error("Ошибка преджевременного выхода из event loop")
            raise
        except Exception as e:
            c = "ошибка на стороне сервера, связанная с отправкой данных: " + str(e)
            logging.error(type(e))
            logging.error(c)
            time.sleep(1)


    async def start_server(self, stop_event):
        try:
            # async with websockets.serve(handler, "192.168.14.2", 8765, ssl=ssl_context):
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            ssl_context.load_cert_chain(certfile="/var/www/panda-back/wscert/server.crt", keyfile="/var/www/panda-back/wscert/server.key")
            async with websockets.serve(self.handler, "192.168.74.105", 8765, max_size=2**62, ssl=ssl_context):
                 # await stop_event.wait()
                 await asyncio.Future()  # Бесконечное ожидание
        except Exception as e:
            logging.error("Ошибка запуска сервера: " + str(e))

    def start_loop(self):
        stop_event = asyncio.Event()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        task = loop.create_task(self.start_server(stop_event))
        try:
            result = loop.run_until_complete(task)
        except asyncio.CancelledError:
            logging.error("Ошибка преджевременного выхода из event loop")
            raise
        except Exception as e:
            logging.error("Ошибка при запуске event loop: {}".format(e))
            logging.error(type(e))
            logging.error("проверка на незакрытые event loop: {}".format(loop.is_running()))
        finally:
            logging.info("cleaning up")
            tasks = asyncio.gather(*asyncio.Task.all_tasks(loop), return_exceptions=True)
            tasks.cancel()
            loop.run_until_complete(tasks)
            loop.close()

    #ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    #ssl_context.load_cert_chain(certfile="certificate.pem", keyfile="private_key.pem")

    #start_server = websockets.serve(echo, "localhost", 8765, ssl=ssl_context)

    #asyncio.get_event_loop().run_until_complete(start_server)
    #asyncio.get_event_loop().run_forever()

    # openssl genrsa -out private_key.pem 2048
    # openssl req -new -x509 -key private_key.pem -out certificate.pem -days 365
try:
    ws = WS_Server()
    ws.start_loop()
except KeyboardInterrupt:
    logging.info("сервер остановлен вручную")
    sys.exit(0)

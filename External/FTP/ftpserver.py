from pyftpdlib import servers
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.authorizers import DummyAuthorizer

# Аутефикация
ser = DummyAuthorizer()
# Добавление нового пользователя
# (имя пользователя, пароль, папка, в которую будут приходить файлы, perm отвечает за возможности клиента
ser.add_user('user_name', 'password', '.', perm='wr')
# создание анонимного пользователя
ser.add_anonymous("./files_to_parse")
# Обработчиком пришедшей информации является FTPHandler
handler = FTPHandler
handler.authorizer = ser
# Хост и порт сервера
address = ('192.168.74.72', 21)
# Создание FTP сервера с определенным адресом и определенным обработчиком
server = servers.FTPServer(address_or_socket=address, handler=FTPHandler)
server.serve_forever()

# Прием файлов
data = server.recv(30)
# В data записан путь к файлу
print(data)
 
# Отправка файлов
data_2 = "the_latest_data.xml"
server.send(data)
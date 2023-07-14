import ftplib
from config import *
from External.DATABASE.database import *


def downloader():
    # Подключение к серверу
    session = ftplib.FTP(ftp_server_ip)
    session.login('', '') #пустое если не нужен логин и пароль
    session.cwd("")
    # Выбор кодировки
    session.encoding = 'utf-8'
    all_files = session.nlst() #список содержимого нужного каталога
    parsed_files = Connection.session.query(Parsed_data.file_name).all() #список файлов, которые уже подверглись парсингу
    for j in range(len(parsed_files)-1, -1, -1): #оставить только файлы, которые не прошли парсинг
        for i in range(len(all_files)-1, -1, -1):
            if len(all_files) > 0:
                if all_files[i] == parsed_files[j][0]:
                    all_files.pop(i)
    for _ in range(len(all_files)):
        f = Parsed_data(file_name = all_files[_])
        Connection.session.add(f)
        Connection.session.commit()
    # Получение бинарных файлов
    for file_name in all_files:
        with open(os.path.abspath(
                os.path.join(BASE_DIR, EXTERNAL_DIR, DATA_DIR, INCOMING_DATA_DIR, file_name)), 'w', encoding="UTF-8") as local_file:
            session.retrlines('RETR ' + file_name, local_file.write)
    # Завершение сессии
    session.quit()

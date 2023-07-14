import os
import json
#https://habr.com/ru/company/otus/blog/549814/
#https://habr.com/ru/company/domclick/blog/589815/
# адрес ftp сервера
ftp_server_ip = "192.168.74.72"
# адрес базы данных
# database_addr = 'postgresql+psycopg2://postgres:Joker_171@localhost:5432/database_for_parser'
database_addr = 'postgresql+psycopg2://postgres:123qweasd@192.168.74.71:5432/database_for_parser'
# cd Пути
BASE_DIR = os.path.dirname(__file__)
INTERNAL_DIR = "Internal"
EXTERNAL_DIR = "External"
DATA_DIR = "DATA"
DATABASES_DIR = "DATABASE"
SERVICES_DATA_DIR = "SERVICES_DATA"
PARSER_DIR = "PARSER"
INCOMING_DATA_DIR = "INCOMING_DATA"
OUTPUT_DATA_DIR = "OUTPUT_DATA"
ADDITIONAL_FILE_DIR = "ADDITIONAL_DATA"
FTP_DIR = "FTP"
API_DIR = "API"
WS_DIR = "WS_SERVER"

# Имена
INCOMING_XML_NAME = "PovodN3.xml"
PARSED_DATA_NAME = "parsed_data.json"
NEW_XML_NAME = "created.xml"
ADDITIONAL_INFO_NAME = "additional_information.json"
TABLE_NAMES_NAME = "table_names_dict.json"
SOME_SHIT_NAME = "some_shit.json"
FILES_FROM_SERVICES = "files_from_services.json"
PREDEFINED_DATA_NAME = "predefined_data.json"

# NSMAP для сборки XML
NSMAP = {
    "V8Exch": "http://www.1c.ru/V8/1CV8DtUD/",
    "core": "http://v8.1c.ru/data",
    "v8": "http://v8.1c.ru/8.1/data/enterprise/current-config",
    "xs": "http://www.w3.org/2001/XMLSchema",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance"
}  # изменяемое ли пространство имен или нет?
NSMAP_1 = {
    None:"http://v8.1c.ru/8.1/data/enterprise"
}
NSMAP_2 = {
    "d6p1": "http://v8.1c.ru/8.1/data/core"
}
NSMAP_3 = {
    None: "http://v8.1c.ru/8.1/data/core"
}
# словари для перевода
translate_table = ''.maketrans({"а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "|yo|",
                                "ж": "|zh|", "з": "z", "и": "i", "й": "j", "к": "k", "л": "l", "м": "m",
                                "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
                                "у": "u", "ф": "f", "х": "h", "ц": "c", "ч": "|ch|", "ш": "|sh|", "щ": "|wch|",
                                "ъ": '|bb|', "ы": "y", "ь": '|j|', "э": "|eh|", "ю": "|yu|",
                                "я": "|ya|", 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё':
                                '|YO|', 'Ж': '|ZH|', 'З': 'Z', 'И': 'I', 'Й': 'J', 'К': 'K', 'Л': 'L', 'М': 'M',
                                'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T',
                                'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'C', 'Ч': '|CH|', 'Ш': '|SH|', 'Щ': '|WCH|',
                                'Э': '|EH|', 'Ю': '|YU|', 'Я': '|YA|', 'Ь': '|J|', 'Ъ': '|BB|', 'Ы': 'Y'
                                })  # \ используется как спецсимвол для обозначения сочетаний букв в ангийской
# транслитерации сначала нужно определить язык входной строки. Исходя из выгрузок достаточно будет определить наличие
# русских букв тегах
vice_verse_translate_table = {"a": "а", "b": "б", "v": "в", "g": "г", "d": "д", "e": "е", "|yo|": "ё",
                              "|zh|": "ж", "z": "з", "i": "и", "j": "й", "k": "к", "l": "л", "m": "м",
                              "n": "н", "o": "о", "p": "п", "r": "р", "s": "с", "t": "т",
                              "u": "у", "f": "ф", "h": "х", "c": "ц", "|ch|": "ч", "|sh|": "ш", "|wch|": "щ",
                              '|bb|': 'ъ', "y": "ы", "|j|": 'ь', "|eh|": "э", "|yu|": "ю", "|ya|": "я", "x": "кс",
                              "w": "в",
                              'A': 'А', 'B': 'Б', 'V': 'В', 'G': 'Г', 'D': 'Д', 'E': 'Е', '|YO|':
                                  'Ё', '|ZH|': 'Ж', 'Z': 'З', 'I': 'И', 'J': 'Й', 'K': 'К', 'L': 'Л',
                              'M': 'М', 'N': 'Н', 'O': 'О', 'P': 'П', 'R': 'Р', 'S': 'С', 'T': 'Т',
                              'U': 'У', 'F': 'Ф', 'H': 'Х', 'C': 'Ц', '|CH|': 'Ч', '|SH|': 'Ш', '|WCH|': 'Щ',
                              '|EH|': 'Э', '|YU|': 'Ю', '|YA|': 'Я', '|J|': 'Ь', '|BB|': 'Ъ', 'Y': 'Ы', "X": "КС",
                              "W": "В"
                              }  # словарь для обратного перевода

# IP адреса для API на консуле
objects_and_addressees_consul = "http://objects-back.service.consul:7008"
personnel_consul = "http://personel-back.service.consul:8085"
toir_consul = "http://toir-back.service.consul:7272"
esi_consul = "http://esi-back.service.consul:5075"
efo_consul = "http://efo-back.service.consul:9020"
nomenclature_consul = "http://nomenclature-back.service.consul:5038"
up_consul = "http://up-back.service.consul:7001"
uk_consul = "http://uk-back.service.consul:7008"

# # IP адреса для API развернутых на локальных машинах
# objects_and_addressees_local = "http://192.168.74.96:5090"
# personnel_local = "http://192.168.74.96:1812"
# toir_local = "http://192.168.74.74:2718"
# up_local = "http://192.168.74.63:7001"
# esi_local = "http://192.168.74.70:5003"
# efo_local = "http://192.168.74.63:9020"
# uk_local = "http://192.168.74.96:5004"
# nomenclature_local = "http://192.168.74.54:5038"

# Адреса для ветки DEV
objects_and_addressees_local = "http://localhost:5090"
personnel_local = "http://localhost:1812"
toir_local = "http://localhost:2718"
up_local = "http://localhost:7001"
esi_local = "http://localhost:5003"
efo_local = "http://localhost:9020"
uk_local = "http://localhost:5004"
nomenclature_local = "http://localhost:5038"

# IP для задания адресов для рассылки на API
# objects_and_addressees_ip = objects_and_addressees_local
# personnel_ip = personnel_local
# toir_ip = toir_local
# up_ip = up_local
# esi_ip = esi_local
# efo_ip = efo_local
# uk_ip = uk_local
# nomenclature_ip = nomenclature_local

# # IP для задания адресов для рассылки на API
objects_and_addressees_ip = objects_and_addressees_consul
personnel_ip = personnel_consul
toir_ip = toir_consul
up_ip = up_consul
esi_ip = esi_consul
efo_ip = efo_consul
uk_ip = uk_consul
nomenclature_ip = nomenclature_consul



SERVICES_LINKS = [
    "{}/EFOAPI/DataExchange/".format(efo_ip),
    "{}/AddresseesAPI/GetData/".format(objects_and_addressees_ip),
    "{}/PersonnelAPI/GetData/".format(personnel_ip),
    "{}/UPAPI/DataExchange/".format(up_ip),
    "{}/NomenclatureAPI/GetData/".format(nomenclature_ip),
    "{}/UKAPI/GetData/".format(uk_ip),
    "{}/ESIAPI/DataExchange/".format(esi_ip)
]

# Задание заголовка запроса
headers = {"Content-Type": "application/json"}

# создаем и открываем различные нужные файлы
Path_to_created_json = os.path.abspath(os.path.join(BASE_DIR, INTERNAL_DIR, SERVICES_DATA_DIR, PARSED_DATA_NAME))
if os.path.exists(Path_to_created_json):
    if os.path.getsize(Path_to_created_json) != 0:
        with open(Path_to_created_json, 'r', encoding='utf-8') as f:
            latest_json_dict = json.load(f)  # словарь для рассылок, берется из файла с xml после парсинга
else:
    latest_json_dict = {}

Path_to_some_shit_json = os.path.abspath(os.path.join(BASE_DIR, INTERNAL_DIR, ADDITIONAL_FILE_DIR, SOME_SHIT_NAME))
if os.path.exists(Path_to_some_shit_json):
    if os.path.getsize(Path_to_some_shit_json) != 0:
        with open(Path_to_some_shit_json, 'r', encoding='utf-8') as f:
            some_shit_json_dict = json.load(f)  # словарь для для сборщика, перехардкоженый серегин хардкод
else:
    some_shit_json_dict = {}



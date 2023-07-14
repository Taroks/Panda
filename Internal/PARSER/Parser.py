from xml.etree import ElementTree
import re
from lxml import etree
from config import *
from collections import OrderedDict
import gc
from pprint import pprint


class ParseToJson:
    def __init__(self):
        self.final_dict = OrderedDict()
        self.list_of_data_dicts = []
        self.list_of_filter_items = []
        self.check_list = []
        self.str_with_reference = "field_{}_reference_to"
        self.additional_dict = OrderedDict()
        self.additional_filteritems_attrib = OrderedDict()
        self.additional_nsmap = OrderedDict()
        self.additional_dict_for_translations = OrderedDict()

    def get_element_tree(self):
        tip = ""
        data_dict = OrderedDict()
        inner_tables = OrderedDict()
        bejesus_tables = OrderedDict()
        list_of_inner_tables = []
        predefined_data_items = OrderedDict()
        predefined_data_items_list = []
        list_of_repeats = []
        addit_attrib = OrderedDict()
        # выгрузка
        tree = ElementTree.parse(os.path.abspath(os.path.join(BASE_DIR, EXTERNAL_DIR, DATA_DIR, INCOMING_DATA_DIR, INCOMING_XML_NAME)))
        root = tree.getroot()
        for child in root:
            if not re.search(r"PredefinedData", child.tag):
                for table_names in child:
                    for data in table_names:
                        if data.attrib != {}:
                            # Вытаскиваем type из аттибутов полей. Сначала получаем его как значение по ключу (type)
                            # потом убираем namespace
                            attrib = list(data.attrib.values())[0]
                            if data.text is None:  # проверяем на странные аттрибуты (например у пустых тэгов)
                                addit_attrib[self.translator(data.tag.split("}")[1])] = data.attrib
                            if re.search(r":", attrib):
                                tip = self.translator(attrib.split(":")[1])
                        if re.search(r'/', data.tag):  # вложенность уровня названия полей
                            field_name = self.translator(data.tag.split("}")[1])
                        else:
                            field_name = self.translator(data.tag)
                        field_data = data.text
                        # внутренние таблицы в таблицах (чекай выгрузку и пребывай в шоке с количества уровней
                        # вложенности)
                        for inner_table in data:
                            # пришлось отделить filteritem потому что у них другая структура
                            if re.search(r"Filter", inner_table.tag.split("}")[1]):
                                # тут мы как раз собираем filteritem
                                for data_filter in data:
                                    self.parsing_filters(data_filter)
                            if self.list_of_filter_items:
                                if re.search(r"Filter", inner_table.tag.split("}")[1]):
                                    inner_tables[
                                        self.translator(inner_table.tag.split("}")[1])] = self.list_of_filter_items
                                    self.list_of_filter_items = []
                            elif not re.search(r"Filter", inner_table.tag.split("}")[1]):
                                inner_tables = self.get_inner_tables(inner_table, bejesus_tables, inner_tables, tip)
                        if inner_tables != {}:
                            list_of_inner_tables.append(inner_tables)
                            inner_tables = {}
                        if field_name in data_dict.keys():
                            s = data_dict.get(field_name)
                            list_of_inner_tables.extend(s)
                            list_of_repeats.append(field_name)
                        if list_of_inner_tables:
                            data_dict[field_name] = list_of_inner_tables
                            list_of_inner_tables = []
                        else:
                            data_dict[field_name] = field_data
                            if tip != "":
                                data_dict[self.translator(self.str_with_reference.format(data.tag.split("}")[1]))] = tip
                                tip = ""
                    if re.search(r'://', table_names.tag):
                        table_name = self.translator(table_names.tag.split("}")[1])
                    else:
                        table_name = self.translator(table_names.tag)
                    dict_for_check = self.final_dict.copy()
                    if table_name in dict_for_check.keys():
                        self.final_dict[table_name].append(data_dict)
                        data_dict = {}
                    elif table_name not in dict_for_check.keys():
                        self.final_dict[table_name] = [data_dict]
                        data_dict = {}
        self.additional_dict["do_not_translate"] = self.check_list
        self.additional_dict["repeated_fields"] = list_of_repeats
        self.additional_dict["additional_attributes"] = addit_attrib
        self.additional_dict["additional_attributes_in_filteritems"] = self.additional_filteritems_attrib
        self.additional_dict["additional_namespaces"] = self.additional_nsmap
        self.additional_dict["outer_mistakes"] = self.additional_dict_for_translations
        if not os.path.exists(os.path.abspath(os.path.join(BASE_DIR, INTERNAL_DIR, ADDITIONAL_FILE_DIR, ADDITIONAL_INFO_NAME))):
            with open(os.path.abspath(os.path.join(BASE_DIR, INTERNAL_DIR, DATA_DIR, ADDITIONAL_FILE_DIR, ADDITIONAL_INFO_NAME)),
                      "w") as additional_file:
                json.dump(self.additional_dict, additional_file, indent=4, ensure_ascii=False)
        else:
            with open(os.path.abspath(os.path.join(BASE_DIR, INTERNAL_DIR, DATA_DIR, ADDITIONAL_FILE_DIR, ADDITIONAL_INFO_NAME)),
                      "a") as additional_file:
                json.dump(self.additional_dict, additional_file, indent=4, ensure_ascii=False)
        with open(os.path.abspath(os.path.join(BASE_DIR, INTERNAL_DIR, DATA_DIR, SERVICES_DATA_DIR, PARSED_DATA_NAME)), 'w',
                  encoding='utf-8') as f:
            json.dump(self.final_dict, f, indent=4, ensure_ascii=False)
        # обрабатываем PredefinedData
        for element in root.iter("PredefinedData"):
            for subelement in element:
                for item in subelement:
                    predefined_data_items_list.append(item.tag)
                    predefined_data_items_list.append(item.attrib)
                    if item.text is not None:
                        predefined_data_items_list.append([item.text])
                predefined_data_items[subelement.tag] = predefined_data_items_list
                predefined_data_items_list = []
        with open(os.path.abspath(os.path.join(BASE_DIR, INTERNAL_DIR, DATA_DIR, ADDITIONAL_FILE_DIR, PREDEFINED_DATA_NAME)), "w") as pred_data:
            json.dump(predefined_data_items, pred_data, indent=4, ensure_ascii=False)

        # да-да, я понимаю тебя, разработчик этого из будущего, меня тоже бесит это
        # количество уровней вложенности

    def get_inner_tables(self, inner_table, bejesus_tables, inner_tables, tip):
        if inner_table.attrib != {}:
            attrib_0 = list(inner_table.attrib.values())[0]
            if re.search(r":", attrib_0):
                tip = self.translator(attrib_0.split(":")[1])
        for bejesus in inner_table:
            if bejesus.attrib != {}:
                attrib_1 = list(bejesus.attrib.values())[0]
                if re.search(r":", attrib_1):
                    tip = self.translator(attrib_1.split(":")[1])
            bejesus_tables[self.translator(bejesus.tag.split("}")[1])] = bejesus.text
            if tip != "":
                bejesus_tables[self.translator(
                    self.str_with_reference.format(bejesus.tag.split("}")[1]))] = tip
                tip = ""
        if bejesus_tables != {}:
            inner_tables[self.translator(inner_table.tag.split("}")[1])] = bejesus_tables
            bejesus_tables = {}
        else:
            inner_tables[self.translator(inner_table.tag.split("}")[1])] = inner_table.text
            if tip != "":
                inner_tables[self.translator(
                    self.str_with_reference.format(inner_table.tag.split("}")[1]))] = tip
                tip = ""
        return inner_tables

    def parsing_filters(self, data_filter):
        filter_items = {}
        for _ in data_filter:
            if _.attrib != {}:
                attrib_1 = list(_.attrib.values())[0]
                if re.search(r":", attrib_1):
                    tip = self.translator(attrib_1.split(":")[1])
                    self.additional_filteritems_attrib[attrib_1.split(":")[1]] = attrib_1.split(":")[0]
            filter_items[self.translator(_.tag.split("}")[1])] = _.text
            if tip != "":
                filter_items[self.translator(self.str_with_reference.format(_.tag.split("}")[1]))] = tip
                tip = ""
        if list(data_filter[1].attrib.values())[0].split(":")[
            0] not in NSMAP:  # Тут покоится моя нерешенная проблема поиска namespace в аттрибутах элементов
            self.additional_nsmap[list(data_filter[1].attrib.values())[0].split(":")[1]] = \
            list(data_filter[1].attrib.values())[0].split(":")[0]
        self.list_of_filter_items.append(filter_items)

    def translator(self, str_to_translate):
        k = {}
        if re.search(r"[а-яёА-ЯЁ]", str_to_translate):
            translate_ready = str_to_translate.translate(translate_table)
            if re.search(r"[a-zA-Z]", str_to_translate) and not re.search(r"_reference_to",
                                                                          str_to_translate) and not re.search(r"\.",
                                                                                                              str_to_translate):
                k[translate_ready] = str_to_translate
                self.additional_dict_for_translations.update(k)
            return translate_ready
        else:
            if str_to_translate not in self.check_list:
                self.check_list.append(str_to_translate)
            return str_to_translate


class ParseToXml:
    def __init__(self):
        # with open(os.path.abspath(os.path.join(BASE_DIR, INTERNAL_DIR, DATA_DIR, SERVICES_DATA_DIR, PARSED_DATA_NAME)), "r") as f:
        #     self.data_from_services = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(f.read())
        with open(os.path.abspath(os.path.join(BASE_DIR, INTERNAL_DIR, DATA_DIR, SERVICES_DATA_DIR, FILES_FROM_SERVICES)), "r") as f:
            self.data_from_services = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(f.read())
        with open(os.path.abspath(os.path.join(BASE_DIR, INTERNAL_DIR, DATA_DIR, ADDITIONAL_FILE_DIR, ADDITIONAL_INFO_NAME)), "r") as file:
            self.additional_information = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(file.read())
            # файл с ополнительной всякой информацией

    def make_tree(self):
        first_one = etree.Element("{%s}_1CV8DtUD" % NSMAP.get("V8Exch"), nsmap=NSMAP)
        second_one = etree.SubElement(first_one, "{%s}Data" % NSMAP.get("V8Exch"))
        for key in self.data_from_services:  # уровень названия таблиц
            list_of_fields = []
            for note in self.data_from_services[key]:  # уровень целой записи
                for field in note:  # уровень поля в записи, а так же вложенных таблиц
                    if not list_of_fields or field in list_of_fields:
                        third_one = etree.SubElement(second_one,
                                                     "{http://v8.1c.ru/8.1/data/enterprise/current-config}%s" % (
                                                             key.split(".")[0] + "." + self.vice_verse_translator(
                                                         key.split(".")[1])))
                        list_of_fields = [field]
                    if re.search(r"reference_to", field):
                        if note[field] != "":
                            if len(note[field].split(".")) > 1:
                                fourth_one.set("{%s}type" % NSMAP.get("xsi"), "v8:" +
                                               note[field].split(".")[0] + "." + self.vice_verse_translator(
                                    (note[field].split(".")[1])))
                            elif len(note[field].split(".")) == 1:
                                fourth_one.set("{%s}type" % NSMAP.get("xsi"), "xs:" + note[field])
                    elif not re.search(r"reference_to", field):
                        if field not in self.additional_information.get("repeated_fields", ""):
                            if type(note[field]) != list:
                                if type(note[field]) == str and len(note[field]) == 0:
                                    continue
                                fourth_one = etree.SubElement(third_one,
                                                              "{http://v8.1c.ru/8.1/data/enterprise/current-config}%s" % (
                                                                  self.vice_verse_translator(field)))
                            elif type(note[field]) == list and len(note[field]) != 0:
                                fourth_one = etree.SubElement(third_one,
                                                              "{http://v8.1c.ru/8.1/data/enterprise/current-config}%s" % (
                                                                  self.vice_verse_translator(field)))
                        if field in self.additional_information.get("additional_attributes").keys() and not note[field]:
                            for _ in self.additional_information.get("additional_attributes").keys():
                                    if field == _:
                                        kiy = list(
                                            self.additional_information.get("additional_attributes").get(field).keys())[0]
                                        fourth_one.set(kiy,
                                                       self.additional_information.get("additional_attributes").get(
                                                           field).get(kiy))
                        if type(note[field]) != list and type(note[field]) != bool and not note[field] is None:
                            fourth_one.text = str(note[field])
                        elif type(note[field]) != list and not note[field] is None:
                            fourth_one.text = str(note[field])
                        elif note[field] is None:
                            fourth_one.text = None
                        elif note[field] == "":
                            fourth_one.text = None
                        if field not in list_of_fields:
                            list_of_fields.append(field)
                    if type(note[field]) == list and len(note[field]) != 0:
                        if field not in self.additional_information.get("repeated_fields", ""):
                            for inner_table in note[field]:
                                for inner_field in inner_table:
                                    if not re.search(r"FilterItem", inner_field):
                                        if re.search(r"reference_to", inner_field):
                                            if inner_table[inner_field] != "":
                                                if len(inner_table[inner_field].split(".")) > 1:
                                                    fifth_one.set("{%s}type" % NSMAP.get("xsi"),
                                                                  "v8:" + inner_table[inner_field].split(".")[
                                                                      0] + "." + self.vice_verse_translator(
                                                                      (inner_table[inner_field].split(".")[1])))
                                                elif len(inner_table[inner_field].split(".")) == 1:
                                                    fifth_one.set("{%s}type" % NSMAP.get("xsi"),
                                                                  "xs:" + inner_table[inner_field])
                                        elif not re.search(r"reference_to", field):
                                            if re.search(r"ChartOfCharacteristicTypesObject", key):
                                                fifth_one = etree.SubElement(fourth_one,
                                                                             (self.vice_verse_translator(inner_field)),
                                                                             nsmap=NSMAP_3)
                                            else:
                                                fifth_one = etree.SubElement(fourth_one,
                                                                             "{http://v8.1c.ru/8.1/data/enterprise/current-config}%s" % (
                                                                                 self.vice_verse_translator(
                                                                                     inner_field)))
                                            if type(inner_table[inner_field]) != list and type(
                                                    inner_table[inner_field]) != bool and inner_table[
                                                inner_field] is not None:
                                                fifth_one.text = str(inner_table[inner_field])
                                            elif type(inner_table[inner_field]) != list and type(
                                                    inner_table[inner_field]) == bool:
                                                fifth_one.text = str(inner_table[inner_field])
                                            elif inner_table[inner_field] == "":
                                                fifth_one.text = None
                                            elif inner_table[inner_field] == None:
                                                fifth_one.text = None
                                    elif re.search(r"FilterItem", inner_field):
                                        list_of_filter_items = []
                                        for filter_item in inner_table[inner_field]:
                                            for filter_field in filter_item:
                                                if not list_of_filter_items or filter_field in list_of_filter_items:
                                                    fifth_one = etree.SubElement(fourth_one,
                                                                                 "%s" % inner_field, nsmap=NSMAP_1)
                                                    list_of_filter_items = []
                                                    list_of_filter_items.append(filter_field)
                                                if not re.search(r"reference_to", filter_field):
                                                    UUID_PATTERN = re.compile(
                                                        r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)
                                                    if UUID_PATTERN.match(filter_item[filter_field]) and filter_item[
                                                        list(filter_item.keys())[
                                                            list(filter_item.keys()).index(filter_field) + 1]] in \
                                                            self.additional_information["additional_namespaces"].keys():
                                                        sixth_one_shame = filter_field
                                                        sixth_one_shame_text = filter_item[filter_field]
                                                    else:
                                                        sixth_one = etree.SubElement(fifth_one,
                                                                                     self.vice_verse_translator(
                                                                                         filter_field))
                                                        if type(filter_item[filter_field]) != bool and filter_item[
                                                            filter_field] is not None:
                                                            sixth_one.text = self.vice_verse_translator(
                                                                str(filter_item[filter_field]))
                                                        elif type(filter_item[filter_field]) == bool:
                                                            sixth_one.text = str(filter_item[filter_field])
                                                        elif filter_item[filter_field] == "":
                                                            sixth_one.text = None
                                                else:
                                                    if len(filter_item[filter_field].split(".")) > 1:
                                                        sixth_one.set("{%s}type" % NSMAP.get("xsi"),
                                                                      "v8:" + filter_item[filter_field].split(".")[
                                                                          0] + "." + self.vice_verse_translator(
                                                                          filter_item[filter_field].split(".")[1]))
                                                    elif len(filter_item[filter_field].split(".")) == 1:
                                                        if filter_item[filter_field].split(".")[0] in \
                                                                self.additional_information[
                                                                    "additional_namespaces"].keys():
                                                            sixth_one = etree.SubElement(fifth_one,
                                                                                         self.vice_verse_translator(
                                                                                             sixth_one_shame),
                                                                                         nsmap=NSMAP_2)
                                                            if type(filter_item[filter_field]) != bool and filter_item[
                                                                filter_field] is not None:
                                                                sixth_one.text = self.vice_verse_translator(
                                                                    str(sixth_one_shame_text))
                                                            elif type(filter_item[filter_field]) == bool:
                                                                sixth_one.text = str(sixth_one_shame_text)
                                                            elif filter_item[filter_field] == "":
                                                                sixth_one.text = None
                                                        if filter_item[filter_field] in self.additional_information.get(
                                                                "additional_attributes_in_filteritems", ""):
                                                            sixth_one.set("{%s}type" % NSMAP.get("xsi"),
                                                                          self.additional_information.get(
                                                                              "additional_attributes_in_filteritems").get(
                                                                              filter_item[filter_field]) + ":" +
                                                                          filter_item[filter_field])
                        if field in self.additional_information.get("repeated_fields", ""):
                            for inner_table in note[field]:
                                g = etree.Element("{http://v8.1c.ru/8.1/data/enterprise/current-config}%s" % (
                                    self.vice_verse_translator(field)))
                                for inner_field in inner_table:
                                    if re.search(r"reference_to", inner_field):
                                        if len(inner_table[inner_field].split(".")) > 1:
                                            fifth_one.set("{%s}type" % NSMAP.get("xsi"),
                                                          "v8:" + inner_table[inner_field].split(".")[
                                                              0] + "." + self.vice_verse_translator(
                                                              (inner_table[inner_field].split(".")[1])))
                                        elif len(inner_table[inner_field].split(".")) == 1:
                                            fifth_one.set("{%s}type" % NSMAP.get("xsi"),
                                                          "v8:" + inner_table[inner_field])
                                    elif not re.search(r"reference_to", field):
                                        fifth_one = etree.SubElement(g,
                                                                     "{http://v8.1c.ru/8.1/data/enterprise/current-config}%s" % (
                                                                         self.vice_verse_translator(inner_field)))
                                        if type(inner_table[inner_field]) == str:
                                            fifth_one.text = inner_table[inner_field]
                                    third_one.append(g)
        # добавляем predefined data в конец
        with open(os.path.abspath(os.path.join(BASE_DIR, INTERNAL_DIR, DATA_DIR, ADDITIONAL_FILE_DIR, PREDEFINED_DATA_NAME)), "r") as pred_data:
            predefined_data = json.load(pred_data)
        a = etree.Element("PredefinedData")
        for _ in predefined_data:
            b = etree.SubElement(a, _)
            for i in predefined_data[_]:
                if type(i) == str:  # так задан тэг
                    c = etree.SubElement(b, i)
                elif type(i) == dict:  # так задан аттрибут
                    for j in i:
                        c.set(j, i[j])
                elif type(i) == list:  # так задан текст
                    c.text(i)
        first_one.append(a)
        tree = etree.ElementTree(first_one)
        return tree

    def make_xml(self):
        self.make_tree().write(os.path.abspath(os.path.join(BASE_DIR, EXTERNAL_DIR, DATA_DIR, OUTPUT_DATA_DIR, NEW_XML_NAME)),
                               pretty_print=True, encoding="UTF-8", xml_declaration=True)
        with open(os.path.abspath(os.path.join(BASE_DIR, EXTERNAL_DIR, DATA_DIR, OUTPUT_DATA_DIR, NEW_XML_NAME)), "rb") as xml_with_utf:
            omaeva = xml_with_utf.read()
        decoded = omaeva.decode("utf-8")
        encoded_with_bom = decoded.encode("utf-8-sig")
        with open(os.path.abspath(os.path.join(BASE_DIR, EXTERNAL_DIR, DATA_DIR, OUTPUT_DATA_DIR, NEW_XML_NAME)), "wb") as xml_with_utf_bom:
            xml_with_utf_bom.write(encoded_with_bom)

    def vice_verse_translator(self, str_to_translate):
        if not re.search(r"[а-яёА-ЯЁ]", str_to_translate):
            if not re.search(r"[^a-zA-Z0-9\|\_]", str_to_translate):
                if not re.search(r"\d", str_to_translate):
                    if str_to_translate not in self.additional_information.get("do_not_translate", ""):
                        translate_ready = ""
                        if str_to_translate in self.additional_information.get("outer_mistakes"):
                            translate_ready = self.additional_information.get("outer_mistakes").get(str_to_translate)
                            return translate_ready
                        while str_to_translate != '':
                            if str_to_translate[0] != "|" and str_to_translate[0] != "_":
                                translated_char = vice_verse_translate_table[str_to_translate[0]]
                                str_to_translate = str_to_translate[1:]
                            elif str_to_translate[0] == "|":
                                auxilliary = re.match(r'\|\w+\|', str_to_translate)
                                translated_char = vice_verse_translate_table[auxilliary.group()]
                                str_to_translate = str_to_translate[auxilliary.end():]
                            elif str_to_translate[0] == "_":
                                translated_char = "_"
                                str_to_translate = str_to_translate[1:]
                            translate_ready = translate_ready + translated_char
                        return translate_ready
                    else:
                        return str_to_translate
                else:
                    return str_to_translate
            else:
                return str_to_translate
        else:
            return str_to_translate


import linecache
import os
from time import sleep

this_path = os.path.dirname(__file__)
first_elc_lines = "FF\n02\n5A\nE2\n35\nF5\n04\n"


def get_bv_files() -> list:
    """ Получает список полных путей исходных фафйлов с базой ключей МК2012 из папки <2012> """
    mkf_path = this_path+"/2012/"
    list_2012_dir = os.listdir(mkf_path)
    mkf_lst = []
    for elem in list_2012_dir:
        if os.path.splitext(elem)[-1] == ".mkf":
            mkf_lst.append(mkf_path + elem)

    return mkf_lst


def create_key_dict(bv_path: str) -> dict:
    """ Принимает файл базы ключей MK2012. Возвращает словарь с ключами"""
    key_dict = {}
    key_code = ''
    key_code_last = 'none'
    first_line = 8193
    last_line = first_line + 3

    """
    получаем список ключей.
    сравниваем последний полученный ключ из файла с предпоследним. 
    Если они совпадают значит пошли пустые ячейки в памяти
    """
    while key_code != key_code_last:
        key_code_last = key_code
        key_code = ''
        # Перебераем
        while first_line <= last_line:
            ln_read = linecache.getline(bv_path, first_line)
            key_code = key_code + ln_read
            first_line += 1

        key_dict.update({key_code: None})
        # обновляем значения линий для следующего ключа
        first_line = first_line + 4
        last_line = last_line + 8

    return key_dict


if __name__ == "__main__":
    mkf_list = get_bv_files()
    key_dict = {}
    for elem in mkf_list:
        new_dict = create_key_dict(elem)
        key_dict.update(new_dict)

    # КОСТЫЛЬ удаляем пустой ключ
    key_dict.pop("FF\nFF\nFF\nFF\n")

    if len(key_dict) > 5000:
        print(f"Ключей больше чем 5000.\nСоздать файл для ELC5000 невозможно.\n"
              f"Завершение работы программы через 20сек.")
        sleep(20)
        exit()

    print(f"Всего ключей для записи: {len(key_dict)}")

    # ПИШИМ КЛЮЧИ В ФАЙЛ
    writeFile = open('elc-new.mkf', 'w')  # открываем файл на запись
    writeFile.write(first_elc_lines)  # пишем в файл 7 служебных строк ELC5000

    for elem in key_dict:  # пишем в файл список ключей
        writeFile.write('01\n' + elem + '01\n')

    # пишем в файл пустые строки до служебной записи с кол-вом ключей
    ffLn = 30018 - 7 - len(key_dict) * 6
    writeFile.write(ffLn * 'FF\n')

    # ДОБОВЛЯЕМ СЛУЖЕБНУЮ ЗАПИСЬ О КОЛ-ВЕ КЛЮЧЕЙ
    # конвертируем кол-во ключей в шестнадцатеричное число, состоящее из 4-х символов
    key_to_hex = "{0:x}".format(len(key_dict) + 1)  # переводим в 16-ричное //кол-во ключей + 1шт.(так нужно для ELC5000)
    key_len_hex = len(key_to_hex)  # узнаём кол-во символов
    hexList = ['', '000', '00', '0', '']  # список с недостающими символами
    hex4simbol = hexList[key_len_hex] + key_to_hex  # делаем число из 4-х символов
    hex_amount = hex4simbol[0:2] + '\n' + hex4simbol[2:4] + '\n'  # итоговое число для файла
    writeFile.write(hex_amount)  # пишем итоговое число в файл

    writeFile.write('FF\n' * 2748)  # добиваем файл пустотой

    writeFile.close()  # закрываем файл

    print("Создан файл <elc-new.mkf>\n\n")
    print("Записывать через метакомовскую прогу MKA\nНастройки:\n"
          "Модель домофона: Неизвестный домофон\nТип носителя: 24CXX\nОбъём памяти: С256\n\n"
          "Окно автоматически закроется через минуту")
    sleep(60)
    
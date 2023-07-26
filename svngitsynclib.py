import os
import shutil
import fnmatch


# Удаление финального слеша в URL репо для унификации папок локальных копий репо
def remove_trail_slash(url: str) -> str:
    '''
    Удаляет финальный "/" из переданного URL

    Параметры:
    url (str): URL удаленного репо

    Возвращает: 
    url (str): URL удаленного репо без финального "/"
    '''
    if url.endswith('/'):
        url = url[:-1]
    return url


# Проверка на существование/создание папок для локальных копий репо
def make_data_dir(dir: str, descr: str):
    '''
    Проверяет, существует ли заданная папка, и создает ее, если нет

    Параметры:
    dir (str): путь к папке
    descr(str): описание папки для логирования в stdout
    '''
    if os.path.isdir(dir) == False:
        print(descr, "(", dir, "): не обнаружена", sep="")
        try:
            print(descr, "(", dir, "): создание..", sep="")
            os.mkdir(dir)
        except:
            print(descr, "(", dir, "): Ошибка создания", sep="")
            exit(1)
        else:
            print(descr, "(", dir, "): создана успешно", sep="")
    else:
        print(descr, "(", dir, "): обнаружена", sep="")


# Очищение папки с локальной копией репо
def clear_data_dir(dir: str):
    '''
    Очищает папку локальной копии репо

    Параметры:
    dir (str): путь к папке
    '''
    for d in os.scandir(dir):
        if d.is_dir():
            shutil.rmtree(d.path)
        else:
            os.remove(d.path)


# Чтение glob-масок из файлов
def read_glob_file(glob_file: str, descr: str) -> list:
    '''
    Возвращает список масок из заданного файла

    Параметры:
    glob_file (str): путь к файлу с glob-масками
    descr(str): описание файла для логирования в stdout
    '''
    data = []  # Инициализация списка glob-масок
    print(descr, ": чтение...")
    try:
        f = open(glob_file, "r")
    except:
        print(descr, ": ошибка чтения! Будет использован пустой список")
    else:
        while line := f.readline():
            line = line.strip()
            if line.__len__:
                data.append(line)
        f.close()
    print(descr, ": чтение завершено")
    return data


# Создание списка нужных файлов/папок из репо Git
def git_go_mark_undel(dir: str, masks: list) -> tuple:
    '''
    Создает словарь "относительный путь файла/папки": True/False (Оставлять в Git / Нет)
    на основе переданного списка glob-масок

    Параметры:
    dir (str): путь к папке локальной копии репо Git
    masks (list): список glob-масок

    Возвращает:
    files_list (dict): словарь "относительный путь файла/папки": True/False (Оставлять в Git / Нет)
    need (bool): логическая переменная для передачи флага "нужности" папки уровнем выше при выходе из рекурсии
    '''
    need = False  # Флаг "нужности" родительской папки для передачи на уровень выше при выходе из рекурсии
    need0 = False  # Флаг "нужности" файла/папки в текущей папке
    need1 = False  # Флаг "нужности" дочерней папки
    files_list = {}
    for dirEntry in os.scandir(dir):
        if dirEntry.name != '.git':
            need0 = False
            for mask in masks:
                if fnmatch.fnmatch(dirEntry.name, mask):
                    need0 = True
            files_list[dirEntry.path] = need0

            if dirEntry.is_dir() and files_list[dirEntry.path] == False:
                files_list_, need1 = git_go_mark_undel(dirEntry.path, masks)
                files_list.update(files_list_)
                if need1:
                    files_list[dirEntry.path] = True

            need = need or need0 or need1
    return files_list, need


# Создание списка нужных файлов/папок из репо SVNs
def svn_go_mark_undel(dir: str, masks: list) -> dict:
    '''
    Создает словарь "относительный путь файла/папки": True/False (Оставлять в SVN / Нет)
    на основе переданного списка glob-масок

    Параметры:
    dir (str): путь к папке локальной копии репо SVN
    masks (list): список glob-масок

    Возвращает:
    files_list (dict): словарь "относительный путь файла/папки": True/False (Оставлять в SVN / Нет)
    '''
    need = False  # Флаг "нужности" родительской папки для передачи на уровень выше при выходе из рекурсии
    need0 = False  # Флаг "нужности" файла/папки в текущей папке
    need1 = False  # Флаг "нужности" дочерней папки
    files_list = {}
    for dirEntry in os.scandir(dir):
        if dirEntry.name != '.svn':
            need0 = False
            for mask in masks:
                if fnmatch.fnmatch(dirEntry.name, mask):
                    need0 = True
            files_list[dirEntry.path] = need0

            if dirEntry.is_dir() and files_list[dirEntry.path] == False:
                files_list_ = svn_go_mark_undel(dirEntry.path, masks)
                files_list.update(files_list_)
    return files_list

#!/usr/bin/env python3

# SVN
# branches https://habr.com/ru/articles/120063/
# svn://192.168.0.98/repo/factor-test
# user: user
# pass: pass

# Создать новый репозиторий из командной строки
# user: giteuser
# pass: passpass
# touch README.md
# git init
# git checkout -b main
# git add README.md
# git commit -m "first commit"
# git remote add origin http://192.168.0.98:3000/factor/test.git
# git push -u origin main
#
# Отправка существующего репо из командной строки
# git remote add origin http://192.168.0.98:3000/factor/test.git
# git push -u origin main

# Для работы с файлами/папками
import os
import sys
import shutil
# Для генерации имен папок для локальных репо
import hashlib
# Для разбора параметров комстроки
import argparse
# Для разбора url удаленных репо
from urllib.parse import urlparse
# Для работы с SVN
# apt install python3-svn
# https://pysvn.sourceforge.io/
import pysvn
# Для работы с Git
# apt install python3-git
# https://gitpython.readthedocs.io/en/stable/reference.html
from git.repo import Repo
import svngitsynclib

# Определение внутренних переменных, потом можно вынести в отдельный конфиг
# Имя общей папки для локальных копий репо SVN и Git, не должно быть текущей папкой
common_local_repo_cache = "cache/"
svn_glob_file = "svn.txt"  # Файл glob-масок для SVN
git_glob_file = "git.txt"  # Файл glob-масок для Git


# Определение и парсинг параметров командной строки для получения входных данных,
# возможно включение интерактивного режима
arg_interact = False  # True - для влючения интерактивного режима
parser = argparse.ArgumentParser(
    description="", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-sl", "--svn-linkrepo", required=arg_interact, default="",
    action="store", help="SVN repo URL, ex: svn://svn_repo_url/svn_repo_path")
parser.add_argument("-su", "--svn-user", required=arg_interact,
    default="", action="store", help="SVN repo username")
parser.add_argument("-sp", "--svn-pass", required=arg_interact,
    default="", action="store", help="SVN repo password")
parser.add_argument("-sr", "--svn-rev", required=arg_interact,
    default="", action="store", help="SVN repo revision")
parser.add_argument("-gl", "--git-linkrepo", required=arg_interact, default="", action="store",
    help="Git repo URL, ex: https://git_user:git_pass@git_repo_url/git_repo_path")
config = parser.parse_args()
config.svn_linkrepo = svngitsynclib.remove_trail_slash(config.svn_linkrepo)

# Тестовый блок, чтобы не забивать комстроку
# config.svn_linkrepo = "svn://192.168.0.98/repo/factor-test"
# config.svn_user = "user"
# config.svn_pass = "pass"
# config.svn_rev = "5"
# config.git_linkrepo = "http://giteuser:passpass@192.168.0.98:3000/factor/test.git"

# Проверка входных данных
# Проверка данных из комстроки

if not config.svn_linkrepo.strip():
    print("Ошибка! Не задан URL репо SVN")
    exit(2)

if not config.svn_user.strip():
    print("Ошибка! Не задано имя пользователя для доступа к репо SVN")
    exit(2)

if not config.svn_pass.strip():
    print("Ошибка! Не задан пароль для доступа к репо SVN")
    exit(2)

if not config.svn_rev.strip():
    print("Ошибка! Не задана ревизия репо SVN")
    exit(2)

if not config.git_linkrepo.strip():
    print("Ошибка! Не задан URL репо Git")
    exit(2)

svn_urlcheck = urlparse(config.svn_linkrepo.strip())
if svn_urlcheck.scheme != 'svn':
    print('Ошибка! протокол для SVN задан: ',
          svn_urlcheck.scheme, '://, ожидается: svn://', sep='')
    exit(2)

# Проверка на совпадающие записи в файлах с glob-масками исключений
# Список glob-масок для SVN
svn_glob_list = svngitsynclib.read_glob_file(
    svn_glob_file, "SVN, файл с glob-масками")
# Список glob-масок для Git
git_glob_list = svngitsynclib.read_glob_file(
    git_glob_file, "Git, файл с glob-масками")

glob_intersect = []  # Список совпадающих glob-масок для SVN и Git
for i in svn_glob_list:
    if i in git_glob_list and i not in glob_intersect:
        glob_intersect.append(i)

if len(glob_intersect):
    print("Ошибка! В файлах", svn_glob_file, git_glob_file,
        "не должно быть совпадающих масок. Совпадения: ")
    for i in glob_intersect:
        print("'", i, "'", sep="", end=" ")
    exit(2)

# Проверка/создание общей папки локальных репо
# Относительный путь обей папки локальных копий репо SVN и Git
svngitsynclib.make_data_dir(common_local_repo_cache,
                            "Общая папка для локальных репозиториев")

# Проверка/создание папок локальных репо SVN и Git
# Относительный путь папки локальной копии репо SVN
svn_local_repo_cache = common_local_repo_cache + \
    hashlib.md5(config.svn_linkrepo.encode()).hexdigest() + "/"
svngitsynclib.make_data_dir(
    svn_local_repo_cache, "Папка для локального репозитория SVN")
# Относительный путь папки локальной копии репо Git
git_local_repo_cache = common_local_repo_cache + \
    hashlib.md5(config.git_linkrepo.encode()).hexdigest() + "/"
svngitsynclib.make_data_dir(
    git_local_repo_cache, "Папка для локального репозитория Git")


# SVN
# Обновление локальной копии или
# Выгрузка удаленного репо SVN в локальную папку
svn_repo = pysvn.Client()  # Инициализация, чтобы vscode не ругалась
# Флаг наличия/отутствия локальной копии репо SVN (True/False)
svn_local_repo_found = True
print("SVN, локальная копия: поиск...")

# Обновление локальной копии на нужную ревизию,
# переход к созданию новой копии в случае ошибки
# (можно добавить проверку на совпадение ревизий)
if os.path.isdir(svn_local_repo_cache + ".svn"):
    print("SVN, локальная копия: обнаружена, попытка обновления...")
    try:
        svn_repo.update(svn_local_repo_cache, revision=pysvn.Revision(
            pysvn.opt_revision_kind.number, config.svn_rev))
    except:
        print(
            "SVN, локальная копия: ошибка доступа, копия испорчена, очистка рабочей папки")
        svn_local_repo_found = False
        svngitsynclib.clear_data_dir(svn_local_repo_cache)
    else:
        print("SVN, локальная копия: обновлена, ревизия", config.svn_rev)
else:
    svn_local_repo_found = False

# Создание локальной копии
if not svn_local_repo_found:
    print("SVN, локальная копия: копирование из удаленного репо")
    # Задание логина по-умолчанию для выключения запроса на ввод логина
    svn_repo.set_default_username(config.svn_user)
    # Задание пароля по-умолчанию для выключения запроса на ввод пароля
    svn_repo.set_default_password(config.svn_pass)
    try:
        svn_repo.checkout(config.svn_linkrepo,
            svn_local_repo_cache,
            revision=pysvn.Revision(pysvn.opt_revision_kind.number, config.svn_rev))
    except Exception as e:
        error = str(e)
        if "callback_get_login" in error:
            print("SVN, локальная копия: ошибка авторизации")
        elif "Can't connect to host" in error:
            print("SVN, локальная копия: сервер недоступен")
        elif "No repository found" in error:
            print("SVN, локальная копия: репозиторий не найден")
        elif "No such revision" in error:
            print("SVN, локальная копия: отсутствует ревизия", config.svn_rev)
        else:
            print("SVN, локальная копия: неопознанная ошибка")

        print("SVN, локальная копия: Останов")
        exit(2)
    else:
        print("SVN, локальная копия: копирование из удаленного репо завершено, ревизия", config.svn_rev)


# Git
# Обновление локальной копии или
# Выгрузка удаленного репо Git в локальную папку
# Флаг наличия/отутствия локальной копии репо Git (True/False)
git_local_repo_found = True
git_repo = Repo()
print("Git, локальная копия: поиск...")

# Обновление локальной копии на нужную ревизию,
# переход к созданию новой копии в случае ошибки
# (можно добавить проверку на совпадение ревизий)
if os.path.isdir(git_local_repo_cache + ".git"):
    print("Git, локальная копия: обнаружена, попытка обновления...")
    try:
        git_repo = Repo(git_local_repo_cache)
        git_repo.git.reset('--hard')
        git_repo.git.pull()
    except:
        print(
            "Git, локальная копия: ошибка доступа, копия испорчена, очистка рабочей папки")
        git_local_repo_found = False
        svngitsynclib.clear_data_dir(git_local_repo_cache)
    else:
        print("Git, локальная копия: обновлена")
else:
    git_local_repo_found = False

# Создание локальной копии
if not git_local_repo_found:
    print("Git, локальная копия: копирование из удаленного репо")
    try:
        # git_repo = Repo() # перенесено вверх для выключения отображения ошибки
        git_repo.clone_from(config.git_linkrepo, git_local_repo_cache)
    except Exception as e:
        error = str(e.stderr)
        if "Authentication failed" in error:
            print("Git, локальная копия: ошибка авторизации")
        elif "Couldn't connect to server" in error:
            print("Git, локальная копия: сервер недоступен")
        elif "repository" in error and "not found" in error:
            print("Git, локальная копия: репозиторий не найден")
        else:
            print("Git, локальная копия: неопознанная ошибка")
        print("Git, локальная копия: Останов")
        exit(2)
    else:
        print("Git, локальная копия: копирование из удаленного репо завершено")


# Работа со списками файлов/папок, соответствующих glob-маскам SVN и Git

# Список файлов/папок, которые нельзя удалять из Git репо: git_need_files
# Словарь "относительный путь файла/папки": True/False (Оставлять в Git / Нет)
git_need_files = {}
pwd = os.getcwd()
os.chdir(git_local_repo_cache)
git_need_files, null = svngitsynclib.git_go_mark_undel("./", git_glob_list)
os.chdir(pwd)

# Список файлов/папок, которые надо перенести из SVN в Git: svn_need_files
# Словарь "относительный путь файла/папки": True/False (Копировать в Git / Нет)
svn_need_files = {}
pwd = os.getcwd()
os.chdir(svn_local_repo_cache)
svn_need_files = svngitsynclib.svn_go_mark_undel("./", svn_glob_list)
os.chdir(pwd)

# Проверка на пересечение списков файлов/папок SVN и Git
for files in git_need_files:
    if files in svn_need_files:
        error = git_need_files[files] and svn_need_files[files]
    else:
        error = False
    if error:
        print("Ошибка! В списках файлов/папок найдены общие пути, проверьте настройки")
        exit(1)

# Создание списка файлов/папок для копирования из SVN в Git
svn_files_pack = []  # список файлов/папок для копирования из SVN в Git
for files in svn_need_files:
    if svn_need_files[files]:
        svn_files_pack.append(files[2:])

# Проверка списка файлов/папок для копирования из SVN в Git на наличие содержимого
if " ".join(svn_files_pack).strip() == "":
    print("Список файлов/папок для копирования из SVN в Git: ошибка! Список пустой. Останов")
    exit(0)  # Поставил нулевой код завершения, т.к. отсутствие файлов для переноса не совсем ошибка

# Удаление ненужных файлов/папок ил локального репо Git
print("Удаление ненужных файлов/папок из локального репо Git: ...")
for file in git_need_files:
    if not git_need_files[file]:
        delobj = git_local_repo_cache + file[2:]
        if os.path.isdir(delobj):
            shutil.rmtree(delobj)
        if os.path.isfile(delobj):
            os.remove(delobj)
print("Удаление ненужных файлов/папок из локального репо Git: завершено")

# Копирование файлов/папок для копирования из SVN в Git
print("Копирование файлов/папок из SVN в Git: ...")
pwd = os.getcwd()
os.chdir(svn_local_repo_cache)
try:
    os.system("tar -cf - " + " ".join(svn_files_pack) +
        " | (cd ../../" + git_local_repo_cache + " && tar xf -)")
except:
    print("Копирование файлов/папок из SVN в Git: ошибка!")
    exit(1)
os.chdir(pwd)
print("Копирование файлов/папок из SVN в Git: завершено")

# Обновление удаленного репо Git
print("Обновление удаленного репо Git: SVN репо: ",
    config.svn_linkrepo, ", ревизия: ", config.svn_rev, sep="")
git_repo.git.add(all=True)
git_repo.index.commit("Обновление из SVN репо: " +
    config.svn_linkrepo + ", ревизия: " + config.svn_rev)
try:
    git_repo.git.push()
except Exception as e:
    print("Обновление удаленного репо Git: ошибка!")
    exit(1)

print("Обновление удаленного репо Git: завершено")

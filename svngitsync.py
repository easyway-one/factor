#!/usr/bin/env python3

### SVN
# branches https://habr.com/ru/articles/120063/
# svn://192.168.0.98/repo/factor-test
# user: user
# pass: pass

### Создать новый репозиторий из командной строки
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
### Отправка существующего репо из командной строки
# git remote add origin http://192.168.0.98:3000/factor/test.git
# git push -u origin main

# Для работы с файлами/папками
import os, sys, shutil
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

### Определение внутренних переменных, потом можно вынести в отдельный конфиг
common_local_repo_cache = "cache/" # не должно быть текущей папкой
svn_glob_file = "svn.txt"
git_glob_file = "git.txt"



### Определение и парсинг параметров командной строки для получения входных данных, 
# возможно включение интерактивного режима
arg_interact = False # True - для влючения интерактивного режима
parser = argparse.ArgumentParser(description="", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-sl", "--svn-linkrepo", required=arg_interact, default="''", action="store", help="SVN repo URL, ex: svn://svn_repo_url/svn_repo_path")
parser.add_argument("-su", "--svn-user", required=arg_interact, default="''", action="store", help="SVN repo username")
parser.add_argument("-sp", "--svn-pass", required=arg_interact, default="''", action="store", help="SVN repo password")
parser.add_argument("-sr", "--svn-rev", required=arg_interact, default="''", action="store", help="SVN repo revision")
parser.add_argument("-gl", "--git-linkrepo", required=arg_interact, default="''", action="store", help="Git repo URL, ex: https://git_user:git_pass@git_repo_url/git_repo_path")
config = parser.parse_args()
config.svn_linkrepo = svngitsynclib.remove_trail_slash(config.svn_linkrepo)

# Тестовый блок, чтобы не забивать комстроку
config.svn_linkrepo = "svn://192.168.0.98/repo/factor-test"
config.svn_user = "user"
config.svn_pass = "pass"
config.svn_rev = "2"
config.git_linkrepo = "http://giteuser:passpass@192.168.0.98:3000/factor/test.git"

### Проверка входных данных
# Проверка данных из комстроки
svn_urlcheck = urlparse(config.svn_linkrepo)
if svn_urlcheck.scheme != 'svn':
  print('Ошибка! протокол для SVN задан: ', svn_urlcheck.scheme, '://, ожидается: svn://', sep='')
  exit(2)

# Проверка на совпадающие записи в файлах с glob-масками исключений
svn_glob_list = svngitsynclib.read_glob_file(svn_glob_file)
git_glob_list = svngitsynclib.read_glob_file(git_glob_file)

glob_intersect = []
for i in svn_glob_list:
  if i in git_glob_list and i not in glob_intersect:
    glob_intersect.append(i)

if len(glob_intersect):
  print("Ошибка! В файлах", svn_glob_file, git_glob_file, "не должно быть совпадающих масок. Совпадения: ")
  for i in glob_intersect:
    print("'", i, "'", sep="", end=" ")
  exit(2)


# Проверка/создание общей папки локальных репо
svngitsynclib.make_data_dir(common_local_repo_cache, "Общая папка для локальных репозиториев")

# Проверка/создание папок локальных репо SVN и Git
svn_local_repo_cache = common_local_repo_cache + hashlib.md5(config.svn_linkrepo.encode()).hexdigest() + "/"
svngitsynclib.make_data_dir(svn_local_repo_cache, "Папка для локального репозитория SVN")
git_local_repo_cache = common_local_repo_cache + hashlib.md5(config.git_linkrepo.encode()).hexdigest() + "/"
svngitsynclib.make_data_dir(git_local_repo_cache, "Папка для локального репозитория Git")


### SVN 
# Обновление локальной копии или
# Выгрузка удаленного репо SVN в локальную папку
svn_repo = pysvn.Client()
svn_local_repo_found = True
print("SVN, локальная копия: поиск...")

# Обновление локальной копии на нужную ревизию, 
# переход к созданию новой копии в случае ошибки 
# (можно добавить проверку на совпадение ревизий)
if os.path.isdir(svn_local_repo_cache + ".svn"):
  print("SVN, локальная копия: обнаружена, попытка обновления...")
  try:
    svn_repo.update(svn_local_repo_cache, revision=pysvn.Revision(pysvn.opt_revision_kind.number, config.svn_rev))
  except:
    print("SVN, локальная копия: ошибка доступа, копия испорчена, очистка рабочей папки")
    svn_local_repo_found = False
    svngitsynclib.clear_data_dir(svn_local_repo_cache)
  else:
    print("SVN, локальная копия: обновлена, ревизия", config.svn_rev)
else:
  svn_local_repo_found = False
  
# Создание локальной копии
if not svn_local_repo_found:
  print("SVN, локальная копия: копирование из удаленного репо")
  svn_repo.set_default_username(config.svn_user)
  svn_repo.set_default_password(config.svn_pass)
  try:
    svn_repo.checkout(config.svn_linkrepo, 
      svn_local_repo_cache,
      revision=pysvn.Revision(pysvn.opt_revision_kind.number, config.svn_rev))
  except Exception as e:
    e = str(e)
    if "callback_get_login" in e:
      print("SVN, локальная копия: ошибка авторизации")
    elif "Can't connect to host" in e:
      print("SVN, локальная копия: сервер недоступен")
    elif "No repository found" in e:
      print("SVN, локальная копия: репозиторий не найден")
    elif "No such revision" in e:
      print("SVN, локальная копия: отсутствует ревизия", config.svn_rev)
    else:
      print("SVN, локальная копия: неопознанная ошибка")

    print("SVN, локальная копия: Останов")
    exit(2)
  else:
    print("SVN, локальная копия: копирование из удаленного репо завершено, ревизия", config.svn_rev)
    

### Git
# Обновление локальной копии или
# Выгрузка удаленного репо Git в локальную папку
git_local_repo_found = True
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
    print("Git, локальная копия: ошибка доступа, копия испорчена, очистка рабочей папки")
    git_local_repo_found = False
    svngitsynclib.clear_data_dir(git_local_repo_cache)
  else:
    print("Git, локальная копия: обновлена")
else:
  git_local_repo_found = False

#exit(0)
# Создание локальной копии
if not git_local_repo_found:
  print("Git, локальная копия: копирование из удаленного репо")
  try:
    git_repo = Repo()
    git_repo.clone_from(config.git_linkrepo, git_local_repo_cache)
  except Exception as e:
    print(e.stderr)
    if "Authentication failed" in e.stderr:
      print("Git, локальная копия: ошибка авторизации")
    elif "Couldn't connect to server" in e.stderr:
      print("Git, локальная копия: сервер недоступен")
    elif "repository" in e.stderr and "not found" in e.stderr:
      print("Git, локальная копия: репозиторий не найден")
    else:
      print("Git, локальная копия: неопознанная ошибка")
    exit(0)
    print("Git, локальная копия: Останов")
    exit(2)
  else:
    print("Git, локальная копия: копирование из удаленного репо завершено")










exit(0)
shutil.copytree(svn_local_repo_cache, git_local_repo_cache, symlinks=False, ignore=None, dirs_exist_ok=True)
shutil.rmtree(git_local_repo_cache + '.svn', ignore_errors=True)

git_repo.git.add(all=True)
git_repo.index.commit("msg")
origin = git_repo.remote(name='origin')
origin.push()

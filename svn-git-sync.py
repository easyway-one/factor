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

def remove_trail_slash(url: str):
  '''Takes repo URL for removing trailing slash'''
  if url.endswith('/'):
    url = url[:-1]
  return url

def make_data_dir(folder: str, descr: str):
  '''Checks data dir if exists and create if not exists'''
  if os.path.isdir(folder) == False:
    print(descr, "(", folder, "): не обнаружена", sep="")
    try:
      print(descr, "(", folder, "): создание..", sep="")
      os.mkdir(folder)
    except:
      print(descr, "(", folder, "): Ошибка создания", sep="")
      exit(1)
    else:
      print(descr, "(", folder, "): создана успешно", sep="")
  else:
    print(descr, "(", folder, "): обнаружена", sep="")
    
def read_glob_file(glob_file: str):
  '''Read glob-file into array'''
  data = []
  with open(glob_file) as f:
    while line := f.readline().rstrip():
      if line.__len__:
        data.append(line)
  return data
 

# Для работы с файлами/папками
import os
import shutil
# Для генерации имен папок для локальных репо
import hashlib
# Для разбора параметров комстроки
import argparse
# Для разбора url удаленных репо
from urllib.parse import urlparse
# Для работы с SVN
# apt install python3-svn
import pysvn
# Для работы с Git
# apt install python3-git
from git.repo import Repo

# Определение внутренних переменных, потом вынести в отдельный конфиг
common_local_repo_cache = "cache/" # не должно быть текущей папкой
svn_glob_file = "svn.txt"
git_glob_file = "git.txt"



### Определение и парсинг параметров командной строки для получения входных данных, возможно включение интерактивного режима
arg_interact = False # True - для влючения интерактивного режима
parser = argparse.ArgumentParser(description="", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-sl", "--svn-linkrepo", required=arg_interact, default="''", action="store", help="SVN repo URL, ex: svn://svn_repo_url/svn_repo_path")
parser.add_argument("-su", "--svn-user", required=arg_interact, default="''", action="store", help="SVN repo username")
parser.add_argument("-sp", "--svn-pass", required=arg_interact, default="''", action="store", help="SVN repo password")
parser.add_argument("-sr", "--svn-rev", required=arg_interact, default="''", action="store", help="SVN repo revision")
parser.add_argument("-gl", "--git-linkrepo", required=arg_interact, default="''", action="store", help="Git repo URL, ex: https://git_user:git_pass@git_repo_url/git_repo_path")
config = parser.parse_args()
config.svn_linkrepo = remove_trail_slash(config.svn_linkrepo)

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

# Проверка на совпадающие записи в файлах с исключениями
svn_glob_list = read_glob_file(svn_glob_file)
git_glob_list = read_glob_file(git_glob_file)

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
make_data_dir(common_local_repo_cache, "Общая папка для локальных репозиториев")

# Проверка/создание папок локальных репо SVN и Git
svn_local_repo_cache = common_local_repo_cache + hashlib.md5(config.svn_linkrepo.encode()).hexdigest() + "/"
make_data_dir(svn_local_repo_cache, "Папка для локального репозитория SVN")
git_local_repo_cache = common_local_repo_cache + hashlib.md5(config.git_linkrepo.encode()).hexdigest() + "/"
make_data_dir(git_local_repo_cache, "Папка для локального репозитория Git")

# Выгрузка удаленного репо SVN в локальную папку
svnclient = pysvn.Client()
svnclient.set_default_username(config.svn_user)
svnclient.set_default_password(config.svn_pass)
svnclient.checkout(config.svn_linkrepo, 
  svn_local_repo_cache,
  revision=pysvn.Revision(pysvn.opt_revision_kind.number, config.svn_rev))

# Выгрузка удаленного репо Git в локальную папку
git_repo = Repo(git_local_repo_cache)

shutil.copytree(svn_local_repo_cache, git_local_repo_cache, symlinks=False, ignore=None, dirs_exist_ok=True)
shutil.rmtree(git_local_repo_cache + '.svn', ignore_errors=True)

git_repo.git.add(all=True)
git_repo.index.commit("msg")
origin = git_repo.remote(name='origin')
origin.push()

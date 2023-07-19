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

def remove_trail_slash(url: str) -> str:
  '''Takes repo URL for removing trailing slash'''
  if url.endswith('/'):
    url = url[:-1]
  return url

def make_data_dir(folder: str, descr: str):
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
  

# Для работы с файлами/папками
import os
# Для генерации имен папок для локальных репо
import hashlib
# Для разбора параметров комстроки
import argparse
# Для разбора url удаленных репо
from urllib.parse import urlparse
# Для работы с SVN
# apt install python3-svn
import pysvn

common_local_repo_dir = "data/"

### Определение и парсинг параметров командной строки для получения входных данных
parser = argparse.ArgumentParser(description="", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-sl", "--svn-linkrepo", required=False, default="''", action="store", help="SVN repo URL, ex: svn://svn_repo_url/svn_repo_path")
parser.add_argument("-su", "--svn-user", required=False, default="''", action="store", help="SVN repo username")
parser.add_argument("-sp", "--svn-pass", required=False, default="''", action="store", help="SVN repo password")
parser.add_argument("-sr", "--svn-rev", required=False, default="''", action="store", help="SVN repo revision")
parser.add_argument("-gl", "--git-linkrepo", required=False, default="''", action="store", help="Git repo URL, ex: https://git_user:git_pass@git_repo_url/git_repo_path")
config = parser.parse_args()
config.svn_linkrepo = remove_trail_slash(config.svn_linkrepo)
#print(config)

config.svn_linkrepo = "svn://192.168.0.98/repo/factor-test"
config.svn_user = "user"
config.svn_pass = "pass"
config.svn_rev = "1"
config.git_linkrepo = "http://giteuser:passpass@192.168.0.98:3000/factor/test.git"

svn_urlcheck = urlparse(config.svn_linkrepo)
print(svn_urlcheck)

if svn_urlcheck.scheme != 'svn':
  print('Ошибка! протокол для SVN задан: ', svn_urlcheck.scheme, '://, ожидается: svn://', sep='')
  exit(2)

# Создание общей папки локальных репо
make_data_dir(common_local_repo_dir, "Общая папка для локальных репозиториев")

# Создание папок локальных репо SVN и Git
svn_local_repo_dir = common_local_repo_dir + hashlib.md5(config.svn_linkrepo.encode()).hexdigest() + "/"
make_data_dir(svn_local_repo_dir, "Папка для локального репозитория SVN")
git_local_repo_dir = common_local_repo_dir + hashlib.md5(config.git_linkrepo.encode()).hexdigest() + "/"
make_data_dir(git_local_repo_dir, "Папка для локального репозитория Git")

svnclient = pysvn.Client()
svnclient.set_default_username(config.svn_user)
svnclient.set_default_password(config.svn_pass)
#check out the current version of the pysvn project
svnclient.checkout(config.svn_linkrepo, 
  svn_local_repo_dir,
  revision=pysvn.Revision(pysvn.opt_revision_kind.number, config.svn_rev))

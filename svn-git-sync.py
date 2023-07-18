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
### Отправка существующего репозитория из командной строки
# git remote add origin http://192.168.0.98:3000/factor/test.git
# git push -u origin main

def remove_trail_slash(s):
  if s.endswith('/'):
    s = s[:-1]
  return s


import argparse

parser = argparse.ArgumentParser(description="", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-sl", "--svn-linkrepo", required=False, default="''", action="store", help="SVN repo URL, ex: svn://svn_repo_url/svn_repo_path")
parser.add_argument("-su", "--svn-user", required=False, default="''", action="store", help="SVN repo username")
parser.add_argument("-sp", "--svn-pass", required=False, default="''", action="store", help="SVN repo password")
parser.add_argument("-sr", "--svn-rev", required=False, default="''", action="store", help="SVN repo revision")
parser.add_argument("-gr", "--git-repo", required=False, default="''", action="store", help="Git repo URL, ex: https://GIT_USER:GIT_PASS@git_repo_url/git_repo_path")
config = parser.parse_args()
config.svn_linkrepo = remove_trail_slash(config.svn_linkrepo)
print(config.svn_linkrepo)

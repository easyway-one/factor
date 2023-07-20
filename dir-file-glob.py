#!/usr/bin/env python3
# Для работы с файлами/папками

def read_glob_file(glob_file: str):
  '''Read glob-file into array'''
  data = []
  with open(glob_file) as f:
    while line := f.readline().rstrip():
      if line.__len__:
        data.append(line)
  return data

import os
import fnmatch


dir_data = "tmp/"

git_mask_exclude = read_glob_file("git.txt")
svn_mask_exclude = read_glob_file("svn.txt")

#l = glob.glob("**", root_dir=dir_data, recursive=True)

def git_go_mark_undel(dir: str) -> bool:
  need = False
  need0 = False
  need1 = False
  for dirEntry in os.scandir(dir):
    if dirEntry.name != '.git' and dirEntry.name != '.svn':
      need0 = False
      for mask in git_mask_exclude:
        if fnmatch.fnmatch(dirEntry.name, mask):
          need0 = True
      git_need_files[dirEntry.path] = need0
          
      if dirEntry.is_dir() and git_need_files[dirEntry.path] == False:
        if git_go_mark_undel(dirEntry.path):
          need1 = True
          git_need_files[dirEntry.path] = True
    
      #print(dirEntry.path, "-", need0, "+", need1, "=", need0 or need1)
      need = need or need0 or need1
  return need

def svn_go_mark_undel(dir: str) -> bool:
  need = False
  need0 = False
  need1 = False
  for dirEntry in os.scandir(dir):
    if dirEntry.name != '.git' and dirEntry.name != '.svn':
      need0 = False
      for mask in svn_mask_exclude:
        if fnmatch.fnmatch(dirEntry.name, mask):
          need0 = True
      svn_need_files[dirEntry.path] = need0
          
      if dirEntry.is_dir() and svn_need_files[dirEntry.path] == False:
        svn_go_mark_undel(dirEntry.path)
        # if svn_go_mark_undel(dirEntry.path):
        #   need1 = True
        #   svn_need_files[dirEntry.path] = True
    
      #print(dirEntry.path, "-", need0, "+", need1, "=", need0 or need1)
      #need = need or need0 or need1
  #return need

git_need_files = {}
pwd = os.getcwd()
os.chdir(dir_data);    
git_go_mark_undel("./")
os.chdir(pwd)

svn_need_files = {}
pwd = os.getcwd()
os.chdir(dir_data);    
svn_go_mark_undel("./")
os.chdir(pwd)

for files in git_need_files:
  if files in svn_need_files:
    error = git_need_files[files] and svn_need_files[files]
  else:
    error = False
  print(files, error)

# for files in svn_need_files:
#   print(files, svn_need_files[files])

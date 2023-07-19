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

mask_exclude = read_glob_file("svn.txt")
files_list = {}
print(mask_exclude)

#l = glob.glob("**", root_dir=dir_data, recursive=True)

def go_mark_undel(dir: str) -> bool:
  needed = False
  needed0 = False
  needed1 = False
  for dirEntry in os.scandir(dir):
    if dirEntry.name != '.git' and dirEntry.name != '.svn':
      needed0 = False
      for mask in mask_exclude:
        if fnmatch.fnmatch(dirEntry.name, mask):
          needed0 = True
      files_list[dirEntry.path] = needed0
      #print(dirEntry.path, "-", files_list[dirEntry.path])
          
      if dirEntry.is_dir() and files_list[dirEntry.path] == False:
        if go_mark_undel(dirEntry.path):
          needed1 = True
          files_list[dirEntry.path] = True
    
      print(dirEntry.path, "-", needed0, "+", needed1, "=", needed0 or needed1)
      needed = needed or needed0 or needed1
  #needed = needed0 or needed1
  return needed

pwd = os.getcwd()
os.chdir(dir_data);    
go_mark_undel("./")
os.chdir(pwd)

print("---")
#files_list["./k8s"] = True
for files in files_list:
  print(files, files_list[files])

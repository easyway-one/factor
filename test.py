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

import os, shutil, fnmatch


dir_data = "tmp/"

git_mask_exclude = read_glob_file("git.txt")
svn_mask_exclude = read_glob_file("svn.txt")

#l = glob.glob("**", root_dir=dir_data, recursive=True)

def git_go_mark_undel(dir: str, masks):
  need = False
  need0 = False
  need1 = False
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

def svn_go_mark_undel(dir: str, masks):
  need = False
  need0 = False
  need1 = False
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

git_dir_data = "tmp/git/"
git_need_files = {}
pwd = os.getcwd()
os.chdir(git_dir_data);    
git_need_files, null = git_go_mark_undel("./", git_mask_exclude)
os.chdir(pwd)

svn_dir_data = "tmp/svn/"
svn_need_files = {}
pwd = os.getcwd()
os.chdir(svn_dir_data);    
svn_need_files = svn_go_mark_undel("./", svn_mask_exclude)
os.chdir(pwd)

print(git_need_files)
print(svn_need_files)

print(type(dict(git_need_files)))

for files in git_need_files:
  if files in svn_need_files:
    error = git_need_files[files] and svn_need_files[files]
  else:
    error = False
  if error:
    print("error")
    exit(0)
  print(files[2:])

svn_files_pack = []
for files in svn_need_files:
  if svn_need_files[files]:
    svn_files_pack.append(files[2:])

pwd = os.getcwd()
os.chdir(svn_dir_data);    
os.system("tar -cf - " + " ".join(svn_files_pack) + " | (cd ../../" + git_dir_data + " && tar xvf -)")
# os.chdir(pwd)
# shutil.move(svn_dir_data + "patch.tar", git_dir_data + "patch.tar")
# os.chdir(git_dir_data);    
# os.system("tar -xf patch.tar")
# os.remove("patch.tar")
os.chdir(pwd)


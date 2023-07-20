import os, shutil, fnmatch

# Удаление финального слеша в URL репо для унификации папок локальных копий репо
def remove_trail_slash(url: str):
  '''Takes repo URL for removing trailing slash'''
  if url.endswith('/'):
    url = url[:-1]
  return url

# Проверка на существование/создание папок для локальных копий репо
def make_data_dir(dir: str, descr: str):
  '''Checks data dir if exists and create if not exists'''
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
  '''Clears local repo cache'''
  for d in os.scandir(dir):
    if d.is_dir():
      shutil.rmtree(d.path)
    else:
      os.remove(d.path)
  
# Чтение glob-масок из файлов    
def read_glob_file(glob_file: str, descr: str):
  '''Read glob-file into array'''
  data = []
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
def git_go_mark_undel(dir: str, masks):
  '''Makes needful files/dirs in Git repo '''
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

# Создание списка нужных файлов/папок из репо SVNs
def svn_go_mark_undel(dir: str, masks):
  '''Makes needful files/dirs in SVN repo '''
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

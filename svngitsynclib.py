import os, shutil

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

# Очищает папку с локальной копией репо
def clear_data_dir(dir: str):
  '''Clears local repo cache'''
  for d in os.scandir(dir):
    if d.is_dir():
      shutil.rmtree(d.path)
    else:
      os.remove(d.path)
  
# Чтение glob-масок из файлов    
# ДОБАВИТЬ ПРОВЕРКУ НА СУЩЕСТВОВАНИЕ ФАЙЛА И СООБЩЕНИЕ ОБ ИСПОЛЬОВАНИИ ПУСТОГО МАССИВА
def read_glob_file(glob_file: str):
  '''Read glob-file into array'''
  data = []
  with open(glob_file) as f:
    while line := f.readline().rstrip():
      if line.__len__:
        data.append(line)
  return data

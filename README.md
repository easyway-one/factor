# factor
Есть два репозитория:
1. SVN репозиторий
2. Git репозиторий

Необходимо написать скрипт или приложение которое будет:
1. Извлекать код из указанного URL репозитория SVN
2. Заменять извлеченным кодом код в Git репозитории с указанным URL.
    a. Старый код в Git репозитории должен быть удален либо замещен новым кодом.

**Дополнительные требования**
1. Git репозиторий содержит файлы и папки на любом уровне вложенности которые должны остаться неизмененными.
2. Один раз выкачанные репозитории SVN или Git должны оставаться на диске и в дальнейшем только обновляться.
3. Можно указывать разные репозитории.
4. URL репозиториев во входящих параметрах указывает на ветку в репозитории (master, trunk или какая-то ветка).

**Входные параметры**
1. Репозиторий SVN:
    1. URL;
    2. Логин;
    3. Пароль.
2. Репозиторий Git:
    a. URL содержащий логин и пароль.
3. Ревизия репозитория SVN на которую необходимо обновлять код
4. Файл в котором указаны glob маски для файлов и папок которые не должны удаляться из Git. Одна строка - один glob.
5. Файл в котором указаны glob маски для файлов и папок которые должны быть перенесены из SVN репозитория в Git репозиторий.
_Допускаются иные входные параметры по выбору разработчика_

**Требования к коду**
1. Код должен быть покрыт комментариями
2. Код должен журналировать все производимые операции в STDOUT
3. При возникновении ошибок, либо исключений:
    a. в STDOUT должна выводится информация об ошибке, её причине и коде возврата вызываемой системной функции (если применимо).
    b. Код возврата скрипта или функции должен быть ненулевым.
4. Должна быть документирована процедура запуска скрипта или приложения с описанием входных параметров.
5. Код размещается в публичном репозитории, для ревью предоставляется ссылка на репозиторий.

# BigQuery-integrations
Import files from FTP(S), SFTP, MySQL, etc. servers into BigQuery.

## Общая информация

BigQuery-integrations — это простое решение для передачи файлов с серверов в Google BigQuery с помощью Google Cloud функции. 
Это решение, безопасное и несложное в использовании, позволяет автоматически выполнять загрузку данных в таблицы Google BigQuery из файла, который регулярно обновляется на серверах с различными протоколами передачи данных.

В текущей версии поддерживается импорт файлов из серверов:

- [FTP](https://github.com/OWOX/BigQuery-integrations/tree/master/ftp);
- [FTPS](https://github.com/OWOX/BigQuery-integrations/tree/master/ftps);
- [HTTP(s)](https://github.com/OWOX/BigQuery-integrations/tree/master/https);
- [MySQL](https://github.com/OWOX/BigQuery-integrations/tree/master/mysql);
- [SFTP](https://github.com/OWOX/BigQuery-integrations/tree/master/sftp).


## Принцип работы

С помощью HTTP POST запроса вызывается Cloud-функция, которая получает файл с сервера и загружает его в таблицу Google BigQuery.
Если таблица уже существует в выбранном датасете, то она будет перезаписана.

## Требования

- проект в Google Cloud Platform с активированным биллингом;
- доступ с правами на чтение к аккаунту на сервере, где расположен файл;
- доступ на редактирование (роль Редактор данных BigQuery) для сервисного аккаунта Cloud-функции в проекте BigQuery, куда будет загружена таблица;
- HTTP-клиент для выполнения POST запросов, вызывающих Cloud-функцию.

## Настройка и использование

Настройка включает в себя:
- создание Cloud-функции в Google Cloud Platform;
- предоставление Cloud-функции доступов к серверу (где расположен файл) и к таблице в BigQuery (куда будет записан импортируемый файл);
- вызов Cloud-функции через HTTP-клиент.

Подробная документация находится по ссылкам:

- [FTP](https://github.com/OWOX/BigQuery-integrations/tree/master/ftp/README.md);
- [FTPS](https://github.com/OWOX/BigQuery-integrations/tree/master/ftps/README.md);
- [HTTP(s)](https://github.com/OWOX/BigQuery-integrations/tree/master/https/README.md);
- [MySQL](https://github.com/OWOX/BigQuery-integrations/tree/master/mysql/README.md);
- [SFTP](https://github.com/OWOX/BigQuery-integrations/tree/master/sftp/README.md).




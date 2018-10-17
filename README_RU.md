# BigQuery-integrations
Import files (data) from Intercom, FTP(S), SFTP, MySQL, etc. servers into BigQuery.

## Общая информация

BigQuery-integrations — содержит набор python-скриптов для автоматизации импорта данных в [Google BigQuery](https://cloud.google.com/bigquery/) с помощью [Google Cloud функции](https://cloud.google.com/functions/). 

В текущей версии подготовлены скрипты для автоматизации импорта данных в Google BigQuery из таких источников, как:

- [FTP](https://github.com/OWOX/BigQuery-integrations/tree/master/ftp);
- [FTPS](https://github.com/OWOX/BigQuery-integrations/tree/master/ftps);
- [HTTP(s)](https://github.com/OWOX/BigQuery-integrations/tree/master/https);
- [Intercom](https://github.com/OWOX/BigQuery-integrations/tree/master/intercom);
- [MySQL](https://github.com/OWOX/BigQuery-integrations/tree/master/mysql);
- [SFTP](https://github.com/OWOX/BigQuery-integrations/tree/master/sftp).


## Принцип работы

С помощью HTTP POST запроса вызывается Cloud-функция, которая получает файл с сервера и загружает его в таблицу Google BigQuery.
Если таблица уже существует в выбранном датасете, то она будет перезаписана.

## Требования

- проект в Google Cloud Platform с активированным биллингом;
- доступ с правами на чтение к аккаунту на сервере, где расположен файл;
- доступ на редактирование *WRITER* к датасету и выполнение заданий (роль *Пользователь заданий BigQuery*)  для сервисного аккаунта Cloud-функции в проекте BigQuery, куда будет загружена таблица;
- HTTP-клиент для выполнения POST запросов, вызывающих Cloud-функцию.

## Настройка и использование

Настройка включает в себя:
- создание Cloud-функции в Google Cloud Platform;
- предоставление Cloud-функции доступов к серверу (где расположен файл) и к таблице в BigQuery (куда будет записан импортируемый файл);
- вызов Cloud-функции через HTTP-клиент.

Подробная документация находится по ссылкам:

- [FTP](https://github.com/OWOX/BigQuery-integrations/tree/master/ftp/README_RU.md);
- [FTPS](https://github.com/OWOX/BigQuery-integrations/tree/master/ftps/README_RU.md);
- [HTTP(s)](https://github.com/OWOX/BigQuery-integrations/tree/master/https/README_RU.md);
- [Intercom](https://github.com/OWOX/BigQuery-integrations/tree/master/intercom/README_RU.md);
- [MySQL](https://github.com/OWOX/BigQuery-integrations/tree/master/mysql/README_RU.md);
- [SFTP](https://github.com/OWOX/BigQuery-integrations/tree/master/sftp/README_RU.md).

## Вопросы

analytics-dev@owox.com




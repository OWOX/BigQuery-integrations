# Интеграция Google BigQuery и FTPS - серверов

## Общая информация

Модуль **ftps-bq-integration** предназначен для передачи файлов с FTPS - серверов в Google BigQuery с помощью Google Cloud функции. 
Это решение позволяет автоматически выполнять загрузку данных в Google BigQuery из файла, который регулярно обновляется на FTPS - сервере.

## Принцип работы

С помощью HTTP POST запроса вызывается Cloud-функция, которая получает файл с FTPS - сервера и загружает его в таблицу Google BigQuery.
Если таблица уже существует в выбранном датасете, то она будет перезаписана.

## Требования

- проект в Google Cloud Platform с активированным биллингом;
- доступ с правами на чтение к FTPS - аккаунту на сервере, где расположен файл;
- доступ на редактирование *WRITER* к датасету и выполнение заданий (роль *Пользователь заданий BigQuery*) для сервисного аккаунта Cloud-функции в проекте BigQuery, куда будет загружена таблица (см. раздел [Доступы](https://github.com/OWOX/BigQuery-integrations/blob/master/ftps/README_RU.md#Доступы));
- HTTP-клиент для выполнения POST запросов, вызывающих Cloud-функцию.

## Настройка и использование

1. Перейдите в [Google Cloud Platform Console](https://console.cloud.google.com/home/dashboard/) и авторизуйтесь с помощью Google аккаунта, или зарегистрируйтесь, если аккаунта еще нет.
2. Перейдите в проект с активированным биллингом или [создайте](https://cloud.google.com/billing/docs/how-to/manage-billing-account#create_a_new_billing_account) новый биллинг аккаунт для проекта.
3. Перейдите в раздел [Cloud Functions](https://console.cloud.google.com/functions/) и нажмите **СОЗДАТЬ ФУНКЦИЮ**. Обратите внимание, что за использование Cloud-функций взимается [плата](https://cloud.google.com/functions/pricing).
4. Заполните следующие поля:

    **Название**: *ftps-bq-integration* или любое другое подходящее название;

    **Выделенный объем памяти**: *2 ГБ* или меньше, в зависимости от размера обрабатываемого файла;

    **Триггер**: *HTTP*;

    **Исходный код**: *Встроенный редактор*;

    **Среда выполнения**: Python 3.X.
    
5. Скопируйте содержимое файла **main.py** в встроенный редактор, вкладка *main.py*.
6. Скопируйте содержимое файла **requirements.txt** в встроенный редактор, вкладка *requirements.txt*.
7. В качестве **вызываемой функции** укажите *ftps*. 
8. В дополнительных параметрах увеличьте **время ожидания** с *60 сек.* до *540 сек.* или меньшее, в зависимости от размеров обрабатываемого файла.
9. Завершите создание Cloud-функции, нажав на кнопку **Создать**. 

## Доступы

### FTPS

Получите у администраторов вашего FTPS - сервера имя пользователя и пароль, где расположен файл с правами на чтение. 
Убедитесь, что файл может быть получен по стандартному порту управления FTPS-соединением — 21.

### BigQuery

Если проект в [Google Cloud Platform Console](https://console.cloud.google.com/home/dashboard/), в котором расположена Cloud-функция и проект в BigQuery — одинаковые — никаких дополнительных шагов не требуется.

В случае, если проекты разные:
1. Перейдите в раздел [Cloud Functions](https://console.cloud.google.com/functions/) и кликните по только что созданной функции для того, чтобы открыть окно **Сведения о функции**.
2. На вкладке **Общие** найдите поле *Сервисный аккаунт* и скопируйте указанный email.
3. В Google Cloud Platform перейдите в IAM и администрирование - [IAM](https://console.cloud.google.com/iam-admin/iam) и выберите проект, в который будет загружена таблица в BigQuery. 
4. **Добавьте участника** - скопированный email и укажите для него роль - *Редактор данных BigQuery*. Сохраните участника.
5. Перейдите к датасету в проекте BigQuery и выдайте доступ на редактирование для сервисного аккаунта. Необходимо [предоставить](https://cloud.google.com/bigquery/docs/datasets#controlling_access_to_a_dataset) *WRITER* доступ к датасету.

## Файл

Файл, который необходимо получить с FTPS - сервера может иметь любое подходящее расширение (.json, .txt, .csv), однако он должен быть в одном из следующих форматах: JSON (newline-delimited) или Comma-separated values (CSV). 

Схема для загружаемого файла определяется автоматически в BigQuery. 

Для правильного определения типа DATE, значения этого поля должны использовать разделитель “-” и быть в формате: YYYY-MM-DD .

Для правильного определения типа TIMESTAMP, значения этого поля должны использовать разделитель “-” (для даты) и “:” для времени и быть в формате: YYYY-MM-DD hh:mm:ss ([список](https://cloud.google.com/bigquery/docs/schema-detect#timestamps) доступных возможностей).

### JSON (newline-delimited)

Содержимое файла этого формата должно быть в виде:
```
{"column1": "my_product" , "column2": 40.0}
{"column1": , "column2": 54.0}
…
```
### CSV

Содержимое файла этого формата должно быть в виде:
```
column1,column2
my_product,40.0
,54.0
…
```
Для правильного определения схемы в таблице, первая строка CSV файла — заголовок — должна содержать только STRING значения, в остальных же строках, хотя бы один столбец должен иметь числовые значения.

## Использование

1. Перейдите в раздел [Cloud Functions](https://console.cloud.google.com/functions/) и кликните по только что созданной функции для того, чтобы открыть окно **Сведения о функции**.
2. На вкладке **Триггер** скопируйте *URL-адрес*. 
С помощью HTTP-клиента отправьте POST запрос по этому *URL-адресу*. Тело запроса должно быть в формате JSON:
```
{
   "ftps": 
            {
              "user": "ftps.user_name",
              "psswd": "ftps.password",
              "path_to_file": "ftps://server_host/path/to/file/"
            },
   "bq":
            {
              "project_id": "my_bq_project",
              "dataset_id": "my_bq_dataset",
              "table_id": "my_bq_table",
              "delimiter": ",",
              "source_format": "CSV",
              "location": "US"
            }
}
```

| Параметр | Объект | Описание |
| --- | --- | --- |
| Обязательные параметры |  
| user | ftps | Имя пользователя на FTPS - сервере, для которого есть доступ с правами на чтение. |
| psswd | ftps | Пароль к пользователю user на FTPS - сервере. |
| path_to_file | ftps | Полный путь к файлу на FTPS - сервере. Всегда должен иметь вид: “ftps://host/path/to/file/” |
| project_id | bq | Название проекта в BigQuery, куда будет загружена таблица. Проект может отличаться от того, в котором создана Cloud-функция. |
| dataset_id | bq | Название датасета в BigQuery, куда будет загружена таблица. |
| table_id | bq | Название таблицы в BigQuery, в которую будет загружен файл с FTPS-сервера. |
| delimiter | bq | Разделитель для полей в CSV файле. Параметр обязательный, если для source_format выбрано значение “CSV”. Поддерживаются разделители: “,”, “\|”, “\t” |
| source_format | bq | Формат загружаемого в BigQuery файла. Поддерживаются форматы “NEWLINE_DELIMITED_JSON”, “CSV”. |
| Опциональные параметры |
| location | bq | Географическое расположение таблицы. По умолчанию указан “US”. |

## Работа с ошибками

Каждое выполнение Cloud-функции логируется. Логи можно посмотреть в Google Cloud Platform:

1. Перейдите в раздел [Cloud Functions](https://console.cloud.google.com/functions/) и кликните по только что созданной функции для того, чтобы открыть окно **Сведения о функции**.
2. Кликнете **Посмотреть журналы** и посмотрите наиболее новые записи на уровне *Ошибки, Критические ошибки*.

Обычно эти ошибки связаны с проблемами доступа к FTPS - серверу, доступа к BigQuery или ошибками в импортируемом файле. 

## Ограничения

1. Размер обрабатываемого файла не должен превышать 2 ГБ.
2. Время выполнения Cloud-функции не может превышать 540 сек.

## Пример использования

### Linux 

Вызовите функцию через терминал Linux:

```
curl -X POST https://REGION-PROJECT_ID.cloudfunctions.net/ftps/ -H "Content-Type:application/json"  -d 
    '{ 
        "ftps": 
                {
                    "user": "ftps.user_name",
                    "psswd": "ftps.password",
                    "path_to_file": "ftps://server_host/path/to/file/"
                },
        "bq":
                {
                    "project_id": "my_bq_project",
                    "dataset_id": "my_bq_dataset",
                    "table_id": "my_bq_table",
                    "delimiter": ",",
                    "source_format": "CSV",
                    "location": "US"
                }
    }'
```

### Python
```
from urllib import urlencode
from httplib2 import Http

trigger_url = "https://REGION-PROJECT_ID.cloudfunctions.net/ftps/"
headers = { "Content-Type": "application/json" }
payload = { 
            "ftps": 
                    {
                        "user": "ftps.user_name",
                        "psswd": "ftps.password",
                        "path_to_file": "ftps://server_host/path/to/file/"
                    },
            "bq":
                    {
                        "project_id": "my_bq_project",
                        "dataset_id": "my_bq_dataset",
                        "table_id": "my_bq_table",
                        "delimiter": ",",
                        "source_format": "CSV",
                        "location": "US"
                    }
            }
Http().request(trigger_url, "POST", urlencode(payload), headers = headers)
```

### [Google Apps Script](https://developers.google.com/apps-script/)

Вставьте следующий код со своими параметрами и запустите функцию:

```
function runftps() {
  trigger_url = "https://REGION-PROJECT_ID.cloudfunctions.net/ftps/"
  var payload = { 
                    "ftps": 
                            {
                                "user": "ftps.user_name",
                                "psswd": "ftps.password",
                                "path_to_file": "ftps://server_host/path/to/file/"
                            },
                    "bq":
                            {
                                "project_id": "my_bq_project",
                                "dataset_id": "my_bq_dataset",
                                "table_id": "my_bq_table",
                                "delimiter": ",",
                                "source_format": "CSV",
                                "location": "US"
                            }
  };

  var options = {
                "method": "post",
                "contentType": "application/json",
                "payload": JSON.stringify(payload)
                };

  var request = UrlFetchApp.fetch(trigger_url, options);
}
```

# Интеграция Google BigQuery и [Intercom](https://www.intercom.com/)

## Общая информация

Модуль **intercom-bq-integration** предназначен для автоматизации передачи данных из Intercom в Google BigQuery с помощью Google Cloud функции.
В настоящее время модуль позволяет импортировать из Intercom в Google BigQuery такие сущности, как: users,  companies,  contacts,  admins, conversations, teams, tags, segments.
При этом модуль не поддерживает custom attributes, но это легко исправить. Необходимо: добавить в схему импорта названия и тип полей кастомных полей, а затем удалить из скрипта следующую строку: row.pop("custom_attributes") 


## Принцип работы

С помощью HTTP POST запроса вызывается Cloud-функция, которая получает данные из Intercom, используя [Intercom API](https://developers.intercom.com/intercom-api-reference/reference) и загружает их в соответствующие таблицы Google BigQuery.
Если таблица уже существует в выбранном датасете, то она будет перезаписана.

## Требования

- проект в Google Cloud Platform с активированным биллингом;
- доступ к Intercom с возможностью создания приложений;
- доступ на редактирование *WRITER* к датасету и создание jobs в Google BigQuery (роль *BigQuery Job User*) для сервисного аккаунта Cloud-функции в проекте BigQuery, куда будет загружена таблица (см. раздел [Доступы](https://github.com/OWOX/BigQuery-integrations/blob/master/intercom/README_RU.md#Доступы));
- HTTP-клиент для выполнения POST запросов, вызывающих Cloud-функцию.

## Настройка 

1. Перейдите в [Google Cloud Platform Console](https://console.cloud.google.com/home/dashboard/) и авторизуйтесь с помощью Google аккаунта, или зарегистрируйтесь, если аккаунта еще нет.
2. Перейдите в проект с активированным биллингом или [создайте](https://cloud.google.com/billing/docs/how-to/manage-billing-account#create_a_new_billing_account) новый биллинг аккаунт для проекта.
3. Перейдите в раздел [Cloud Functions](https://console.cloud.google.com/functions/) и нажмите **СОЗДАТЬ ФУНКЦИЮ**. Обратите внимание, что за использование Cloud-функций взимается [плата](https://cloud.google.com/functions/pricing).
4. Заполните следующие поля:

    **Название**: *intercom-bq-integration* или любое другое подходящее название;

    **Выделенный объем памяти**: *2 ГБ* или меньше, в зависимости от размера обрабатываемого файла;

    **Триггер**: *HTTP*;

    **Исходный код**: *Встроенный редактор*;

    **Среда выполнения**: Python 3.X.
5. Скопируйте содержимое файла **main.py** в встроенный редактор, вкладка *main.py*.
6. Скопируйте содержимое файла **requirements.txt** в встроенный редактор, вкладка *requirements.txt*.
7. В качестве **вызываемой функции** укажите *intercom*. 
8. В дополнительных параметрах увеличьте **время ожидания** с *60 сек.* до *540 сек.* или меньшее, в зависимости от размеров обрабатываемого файла.
9. Завершите создание Cloud-функции, нажав на кнопку **Создать**. 

## Доступы

### Intercom

Получите в Intercom Access Token с правами на чтение любых данных. Для этого переходим в Settings → Developers → Create an App. 
Разрешаем читать любые данные (для этого ставим соответствующие галочки). После создания приложения с нужными правами — скопируйте и сохраните Access Token.

### BigQuery

Если проект в [Google Cloud Platform Console](https://console.cloud.google.com/home/dashboard/), в котором расположена Cloud-функция и проект в BigQuery — одинаковые — никаких дополнительных шагов не требуется.

В случае, если проекты разные:
1. Перейдите в раздел [Cloud Functions](https://console.cloud.google.com/functions/) и кликните по только что созданной функции для того, чтобы открыть окно **Сведения о функции**.
2. На вкладке **Общие** найдите поле *Сервисный аккаунт* и скопируйте указанный email.
3. В Google Cloud Platform перейдите в IAM и администрирование - [IAM](https://console.cloud.google.com/iam-admin/iam) и выберите проект, в который будет загружена таблица в BigQuery. 
4. **Добавьте участника** - скопированный email и укажите для него роль - *Пользователь заданий BigQuery*. Сохраните участника.
5. Перейдите к датасету в проекте BigQuery и выдайте доступ на редактирование для сервисного аккаунта. Необходимо [предоставить](https://cloud.google.com/bigquery/docs/datasets#controlling_access_to_a_dataset) *WRITER* доступ к датасету.

## Использование

1. Перейдите в раздел [Cloud Functions](https://console.cloud.google.com/functions/) и кликните по только что созданной функции для того, чтобы открыть окно **Сведения о функции**.
2. На вкладке **Триггер** скопируйте *URL-адрес*. 
С помощью HTTP-клиента отправьте POST запрос по этому *URL-адресу*. Тело запроса должно быть в формате JSON:
```
{
  "intercom": {
    "accessToken": "INTERCOM ACCESS TOKEN",
     "entities": [
            "users", 
            "companies", 
            "contacts", 
            "admins",
            "conversations",
            "teams",
            "tags",
            "segments"
            ]
        },
    "bq": {
        "project_id": "YOUR GCP PROJECT",
        "dataset_id": "YOUR DATASET NAME",
        "location": "US"
     }
}

```

| Параметр | Объект | Описание |
| --- | --- | --- |
| Обязательные параметры |   
| accessToken | intercom | Ваш Access Token к API Intercom. |
| entities | intercom  | Список сущностей в Intercom данные о которых вы хотите импортировать в BigQuery. В примере приведен полный список возможных значений. |
| project_id | bq | Название проекта в BigQuery, куда будет загружена таблица. Проект может отличаться от того, в котором создана Cloud-функция. |
| dataset_id | bq | Название датасета в BigQuery, куда будет загружена таблица. |
| Опциональные параметры |
| location | bq | Географическое расположение таблицы. По умолчанию указан “US”. |

## Работа с ошибками

Каждое выполнение Cloud-функции логируется. Логи можно посмотреть в Google Cloud Platform:

1. Перейдите в раздел [Cloud Functions](https://console.cloud.google.com/functions/) и кликните по только что созданной функции для того, чтобы открыть окно **Сведения о функции**.
2. Кликнете **Посмотреть журналы** и посмотрите наиболее новые записи на уровне *Ошибки, Критические ошибки*.

## Ограничения

1. Размер обрабатываемого файла не должен превышать 2 ГБ.
2. Время выполнения Cloud-функции не может превышать 540 сек.

В случае превышения одного из лимитов вы можете запускать функцию отдельно для каждой сущности Intercom. 
Таким образом, чтобы получить данные для users и contacts — вам необходимо выполнить функцию два раза. Первый раз в entities необходимо передать "users", а второй "contacts".

## Пример использования

### Linux 

Вызовите функцию через терминал Linux:

```
curl -X POST https://REGION-PROJECT_ID.cloudfunctions.net/intercom/ -H "Content-Type:application/json"  -d 
    '{
      "intercom": {
        "accessToken": "INTERCOM ACCESS TOKEN",
        "entities": [
                "users", 
                "companies", 
                "contacts", 
                "admins",
                "conversations",
                "teams",
                "tags",
                "segments"
                ]
            },
        "bq": {
            "project_id": "YOUR GCP PROJECT",
            "dataset_id": "YOUR DATASET NAME",
            "location": "US"
     }
}'
```

### Python

```
from httplib2 import Http
import json

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

trigger_url = "https://REGION-PROJECT_ID.cloudfunctions.net/intercom/"

headers = {"Content-Type": "application/json; charset=UTF-8"}
payload = {
          "intercom": {
            "accessToken": "INTERCOM ACCESS TOKEN",
            "entities": [
                    "users", 
                    "companies", 
                    "contacts", 
                    "admins",
                    "conversations",
                    "teams",
                    "tags",
                    "segments"
                    ]
                },
            "bq": {
                "project_id": "YOUR GCP PROJECT",
                "dataset_id": "YOUR DATASET NAME",
                "location": "US"
             }
}
Http().request(method = "POST", uri = trigger_url, body = json.dumps(payload), headers = headers)
```

### [Google Apps Script](https://developers.google.com/apps-script/)

Вставьте следующий код со своими параметрами и запустите функцию:

```
function runIntercom() {
  trigger_url = "https://REGION-PROJECT_ID.cloudfunctions.net/intercom/"
  payload = {
          "intercom": {
            "accessToken": "INTERCOM ACCESS TOKEN",
            "entities": [
                    "users", 
                    "companies", 
                    "contacts", 
                    "admins",
                    "conversations",
                    "teams",
                    "tags",
                    "segments"
                    ]
                },
            "bq": {
                "project_id": "YOUR GCP PROJECT",
                "dataset_id": "YOUR DATASET NAME",
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

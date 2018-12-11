from google.cloud import bigquery

import os, io
import json, requests

def load_to_gbq(client, data, bq_configuration):
    """
        Loading data to BigQuery using *bq_configuration* settings.
    """
    client = bigquery.Client(project = bq_configuration["project_id"])
    dataset_ref = client.dataset(bq_configuration["dataset_id"])
    table_ref = dataset_ref.table(bq_configuration["table"])

    # determine uploading options
    job_config = bigquery.LoadJobConfig()
    job_config.write_disposition = 'WRITE_TRUNCATE'
    job_config.source_format = "NEWLINE_DELIMITED_JSON"
    job_config.autodetect = True

    load_job = client.load_table_from_file(
        data,
        table_ref,
        job_config = job_config)  # API request
    print('Starting job {}'.format(load_job.job_id))

    load_job.result()  # Waits for table load to complete.
    print('Job finished.')

def entities(amocrm_configuration, auth_cookies, entity):

    print("Entity " + entity + " in progress...")
    response = True
    offset = 0
    data_dumps = ''
    http = amocrm_configuration["apiAddress"] + "/api/v2/" + entity

    while response:
        payload = {
            "limit_rows": 500,
            "limit_offset": offset
        }

        request = requests.get(http, cookies = auth_cookies, params = payload)
        offset += 500

        if request.status_code != 200:
            break

        response = request.json()
        if not response.get("_embedded", {}).get("items"):
            break

        items = response.get("_embedded", {}).get("items")

        for element in items:
            for field in ("company", "pipeline", "main_contact", "leads", "contacts", "catalog_elements", "customers"):
                element[field].pop("_links") if element.get(field, {}).get("_links") else None
            element.pop("_links") if element.get("_links") else None

            if entity == "customers_periods" and element.get("conditions"):
                element["conditions"] = element["conditions"][0]

            data_dumps += json.dumps(element) + os.linesep

        if entity in ("catalogs", "customers_periods"):
            break

    return data_dumps

def account(amocrm_configuration, auth_cookies):

    print("Account in progress...")

    result = {}
    data_entity = []
    statuses = []

    http = amocrm_configuration["apiAddress"] + "/api/v2/account"

    payload = {
        "with": "users,pipelines,groups"
    }

    request = requests.get(http, cookies = auth_cookies, params = payload)

    if request.content:
        response = request.json()
    else:
        return

    response.pop("_links") if response.get("_links") else None
    embedded = response.get("_embedded")

    for entity in list(embedded.keys()):
        current_entity = embedded[entity]
        if isinstance(current_entity, list):
            for data in current_entity:
               data.pop("_links") if data.get('_links') else None
            result[entity] = current_entity
            continue

        for data in current_entity:
            current_entity[data].pop("_links") if current_entity[data].get('_links') else None
            if entity == "pipelines":
                 statuses_dict = current_entity[data]["statuses"]
                 for status in statuses_dict:
                     statuses.append(statuses_dict[status])
                 current_entity[data]["statuses"] = statuses
            data_entity.append(current_entity[data])
        result[entity] = data_entity
        data_entity = []

    response.pop("_embedded")
    response.update(result)

    return json.dumps(response)


def amocrm(request):
    """
        Function to execute.
    """
    try:
        # get POST data from Flask.request object
        request_json = request.get_json()
        amocrm_configuration = request_json["amocrm"]
        bq_configuration = request_json["bq"]

        if not bq_configuration.get("location"):
            bq_configuration["location"] = "US"

        # authorization data
        auth_payload = {
            "USER_LOGIN": amocrm_configuration["user"],
            "USER_HASH": amocrm_configuration["apiKey"],
            "type": "json"
        }

    except Exception as error:
        message = "An error occurred with POST request data. Details: " + os.linesep + str(error)
        print(message)
        raise SystemExit

    try:
        authorization = requests.post(amocrm_configuration["apiAddress"] + "private/api/auth.php", data = auth_payload)
        auth_cookies = authorization.cookies
        
        if authorization.status_code != 200:
            error_response = authorization.json()
            message = "Authorization error occurred. Error: " + error_response.get('response', {}).get('error') + os.linesep
            message += "Code: " + str(error_response.get('response', {}).get('error_code'))
            print(message)

        client = bigquery.Client(project = bq_configuration["project_id"])
    except Exception as error:
        message = "Authorization error occurred. " + os.linesep + str(error)
        print(message)
        raise SystemExit

    for entity in amocrm_configuration["entities"]:
        try:
            if entity == "account":
                amocrm_data = account(amocrm_configuration, auth_cookies)
            else:
                amocrm_data = entities(amocrm_configuration, auth_cookies, entity)

            # upload file to the BigQuery
            file_raw = amocrm_data.encode('utf-8')
            file = io.BytesIO(file_raw)
            bq_configuration["table"] = entity
            load_to_gbq(client, file, bq_configuration)
        except Exception as error:
            message = "An error occurred trying to process " + entity + os.linesep + str(error)
            print(message)

    print("All tasks have been completed.")

from google.cloud import bigquery
from lxml import etree
import os, re
import json, requests

# writeable part of the filesystem for Cloud Functions instance
gc_write_dir = "/tmp"

def extract_text(element):
    """
        Return *text* attribute of an implied element if available.
    """
    if element is not None:
        return element.text
    else:
        return None

def get_messages(expertsender_configuration):
    """
        Geeting and transforming expertsender Messages using expertsender API: https://sites.google.com/site/expertsenderapiv2/home
    """
    # will contain data from ExpertSender
    data = []
    params = {
        "apiKey": expertsender_configuration["apiKey"],
        "startDate": expertsender_configuration["date"],
        "endDate": expertsender_configuration["date"]
    }

    # Build get request
    request = requests.get(expertsender_configuration["apiAddress"] + "Api/Messages", params = params)
    if request.status_code != 200:
        message = "En error occured requesting expertsender API method: Messages. The process has finished with code " + str(request.status_code) + "." + os.linesep
        message += request.content
        print(message)
        return

    # parse xml-response
    xml_response = etree.fromstring(request.content)

    # get Messages element
    try:
        Messages = xml_response[0][0]
        messages = Messages.findall("Message")
    except Exception as error:
        message = "ExpertSender API response can't be processed. Error details: " + str(error)
        return

    # start parse messages
    for message in messages:
        data.append(
            {
                "Id": extract_text(message.find("Id")),
                "FromName": extract_text(message.find("FromName")),
                "FromEmail": extract_text(message.find("FromEmail")),
                "Subject": extract_text(message.find("Subject")),
                "Type": extract_text(message.find("Type")),
                "SentDate": extract_text(message.find("SentDate")),
                "Tags": extract_text(message.find("Tags"))
            }
        )

    # write data in newline delimited JSON file
    if data:
        filename = "Messages.json"
        with open(filename, 'w') as outfile:
            for row in data:
                outfile.write(json.dumps(row) + os.linesep)
        outfile.close()
    else:
        return

    return filename

def get_activities(expertsender_configuration, _type):
    """
        Geeting and transforming expertsender Activities using expertsender API: https://sites.google.com/site/expertsenderapiv2/home
    """
    print("The " + _type + " are processing...")
    params = {
        "apiKey": expertsender_configuration["apiKey"],
        "date": expertsender_configuration["date"],
        "columns": "Extended",
        "returnTitle": True,
        "returnGuid": True,
        "type": _type
    }

    # Build get request
    request = requests.get(expertsender_configuration["apiAddress"] + "Api/Activities", params = params)

    if request.status_code != 200:
        message = "En error occured requesting expertsender API method: Activities. The process has finished with code " + str(request.status_code) + "." + os.linesep
        message += request.content
        print(message)
        return

    response = request.content.decode("utf-8-sig")
    if len(re.findall("\r\n", response)) <= 1:
        message = "No data is in an ExperSender API response."
        print(message)
        return

    # write data in newline delimited JSON file
    filename = _type + ".csv"
    with open(filename, 'w') as outfile:
            outfile.write(response)

    return filename

def load_to_gbq(filename, bq_configuration):
    """
        Loading data to BigQuery using *bq_configuration* settings.
    """
    # construct Client object with the path to the table in which data will be stored
    client = bigquery.Client(project = bq_configuration["project_id"])
    dataset_ref = client.dataset(bq_configuration["dataset_id"])
    table_ref = dataset_ref.table(bq_configuration["table"])

    # determine uploading options
    job_config = bigquery.LoadJobConfig()
    job_config.write_disposition = 'WRITE_TRUNCATE'
    job_config.source_format = bq_configuration["source_format"]
    job_config.autodetect = True
    if bq_configuration["source_format"].upper() == "CSV":
        job_config.skip_leading_rows = 1

    # upload the file to BigQuery table
    with open(filename, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_ref, location = bq_configuration["location"], job_config = job_config)
    job.result()
    print("The Job " + job.job_id + " in status " + job.state + " for table " + bq_configuration["project_id"] + "." +
          bq_configuration["dataset_id"] + "." + bq_configuration["table"] + ".")
    os.remove(filename)

def expertsender(request):
    """
        Function to execute.
    """
    entities_list = []

    try:
        # get POST data from Flask.request object
        request_json = request.get_json()
        expertsender_configuration = request_json["expertsender"]
        bq_configuration = request_json["bq"]

        if not bq_configuration.get("location"):
            bq_configuration["location"] = "US"

        # extract entities to process
        for entity in expertsender_configuration["entities"]:
            if entity.get("types"):
                for _type in entity.get("types"):
                    entities_list.append((entity.get("entity"), _type))
            else:
                entities_list.append((entity.get("entity"), entity.get("types")))

    except Exception as error:
        message = "An error occured with POST request data." + os.linesep + str(error)
        print(message)
        raise SystemExit

    # go to writable directory
    os.chdir(gc_write_dir)

    # getting data from expertsender
    for entity in entities_list:
        if entity[0] == "Messages":
            print("The Messages data are processing...")
            bq_configuration["source_format"] = "NEWLINE_DELIMITED_JSON"
            bq_configuration["table"] = entity[0] + "_" + expertsender_configuration["date"].replace("-", '')
            try:
                result_file = get_messages(expertsender_configuration)
            except Exception as error:
                message = "An error occured trying to get Messages data from expertsender." + os.linesep + str(error)
                print(message)
                continue

        elif entity[0] == "Activities":
            bq_configuration["source_format"] = "CSV"
            bq_configuration["table"] = entity[1] + "_" + expertsender_configuration["date"].replace("-", '')
            try:
                result_file = get_activities(expertsender_configuration, entity[1])
            except Exception as error:
                message = "An error occured trying to get Acivities data (" + entity[1] + ") from expersender." + os.linesep + str(error)
                print(message)
                continue
        else:
            messages = "Entities specified incorrectly."
            print(messages)
            raise SystemExit

        # upload the file to BigQuery
        if result_file:
            try:
                load_to_gbq(result_file, bq_configuration)
                print("The data has downloaded.")
            except Exception as error:
                message = "An error occured trying to upload " + entity[0] + str((": " + entity[1]) if entity[0] == "Activities" else '') + " data to Google BigQuery." + os.linesep + str(error)
                print(message)

    print("All tasks have been completed.")
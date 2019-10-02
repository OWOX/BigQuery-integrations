from google.cloud import bigquery
import os
import requests as rq

# writeable part of the filesystem for Cloud Functions instance
gc_write_dir = "/tmp"

def get_file_https(path_to_file):
    """
        Get an existing file from HTTP(S) via http(s)://*host*/*path_to_file* link to a home directory.
        The function return the full path to the file that has been downloaded.
    """
    # construct request object and get the file on a server
    request_obj = rq.get(path_to_file)
    results = request_obj.content.decode("utf-8").split("\n")
    file_name = "http.txt"
    with open(file_name, "w") as output_file:
        for row in results:
            output_file.write(row + "\n")

    file_location = gc_write_dir + "/" + file_name
    print("File " + path_to_file + " has got successfully.")
    return file_location

def give_file_gbq(path_to_file, bq_configuration):
    """
        Download file from *path_to_file* to BigQuery table using *bq_configuration* settings.
    """
    # construct Client object with the path to the table in which data will be stored
    client = bigquery.Client(project = bq_configuration["project_id"])
    dataset_ref = client.dataset(bq_configuration["dataset_id"])
    table_ref = dataset_ref.table(bq_configuration["table_id"])

    # determine uploading options
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bq_configuration["source_format"].upper()
    job_config.write_disposition = bq_configuration["write_disposition"]
    if bq_configuration["source_format"].upper() == "CSV":
        job_config.field_delimiter = bq_configuration["delimiter"]
        job_config.skip_leading_rows = 1
    job_config.autodetect = True

    # upload the file to BigQuery table
    with open(path_to_file, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_ref, location = bq_configuration["location"], job_config = job_config)
    job.result()
    print("The Job " + job.job_id + " in status " + job.state + " for table " + bq_configuration["project_id"] + "." + bq_configuration["dataset_id"] + "." + bq_configuration["table_id"] + ".")
    os.remove(path_to_file)

def https(request):
    """
        Function to execute.
    """
    try:
        # get POST data from Flask.request object
        request_json = request.get_json()
        https_configuration = request_json["https"]
        bq_configuration = request_json["bq"]

        if not bq_configuration.get("location"):
            bq_configuration["location"] = "US"
        bq_configuration["write_disposition"] = "WRITE_TRUNCATE"

    except Exception as error:
        print("An error occured with POST request data.")
        print(str(error))
        raise SystemExit

    # go to writable directory
    os.chdir(gc_write_dir)

    # get the file from HTTPS/HTTP
    try:
        https_file = get_file_https(https_configuration["path_to_file"])
    except Exception as error:
        print("An error occured trying to get file from http(s).")
        print(str(error))
        raise SystemExit

    # upload the file to BigQuery
    try:
        give_file_gbq(https_file, bq_configuration)
    except Exception as error:
        print("An error occured trying to upload file to Google BigQuery.")
        print(str(error))

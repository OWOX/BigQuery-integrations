from google.cloud import bigquery
import os, re
import ftplib

# writeable part of the filesystem for Cloud Functions instance
gc_write_dir = "/tmp"

def get_file_ftps(host, path_to_file, ftps_configuration):
    """
        Copy an existing file from FTP via ftp://*host*/*path_to_file* link to home directory.
        The function return the full path to the file that has been downloaded.
    """
    # Construct FTP object and get the file on a server
    with ftplib.FTP_TLS(host, user = ftps_configuration["user"], passwd = ftps_configuration["psswd"]) as ftps:
        filename = re.findall("[^/]*$", path_to_file)[0]
        with open(filename, "wb") as wf:
            ftps.retrbinary("RETR " + filename, wf.write)

    file_location = gc_write_dir + "/" + filename
    print("File " + path_to_file + " has got successfully.")
    return file_location


def give_file_gbq(path_to_file, bq_configuration):
    """
        Download file from *path_to_file* to BigQuery table using *bq_configuration* settings.
    """
    # construct Client object with the path to the table in which data will be stored
    client = bigquery.Client(project=bq_configuration["project_id"])
    dataset_ref = client.dataset(bq_configuration["dataset_id"])
    table_ref = dataset_ref.table(bq_configuration["table_id"])

    # determine uploading options
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bq_configuration["source_format"].upper()
    job_config.write_disposition = bq_configuration["write_disposition"]
    if bq_configuration["source_format"].upper() == "CSV":
        job_config.fieldDelimiter = bq_configuration["delimiter"]
        job_config.skip_leading_rows = 1
    job_config.autodetect = True

    # upload the file to BigQuery table
    with open(path_to_file, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_ref, location=bq_configuration["location"],
                                          job_config=job_config)
    job.result()
    print("The Job " + job.job_id + " in status " + job.state + " for table " + bq_configuration["project_id"] + "." +
          bq_configuration["dataset_id"] + "." + bq_configuration["table_id"] + ".")
    os.remove(path_to_file)

def ftps(request):
    """
        Function to execute.
    """
    try:
        # get POST data from Flask.request object
        request_json = request.get_json()
        ftps_configuration = request_json["ftps"]
        bq_configuration = request_json["bq"]

        if not bq_configuration.get("location"):
            bq_configuration["location"] = "US"
        bq_configuration["write_disposition"] = "WRITE_TRUNCATE"

        host = re.sub("ftps://", "", re.findall("ftps://[^/]*", ftps_configuration["path_to_file"])[0])
        path_to_file = re.sub("/$", "", re.sub("ftps://" + host + "/", "", ftps_configuration["path_to_file"]))
    except Exception as error:
        print("An error occured with POST request data.")
        print(str(error))
        raise SystemExit

    # go to writable directory
    os.chdir(gc_write_dir)

    # get the file from FTPS
    try:
        ftp_file = get_file_ftps(host, path_to_file, ftps_configuration)
    except Exception as error:
        print("An error occured trying to get file from ftps.")
        print(str(error))
        raise SystemExit

    # upload the file to BigQuery
    try:
        give_file_gbq(ftp_file, bq_configuration)
    except Exception as error:
        print("An error occured trying to upload file to Google BigQuery.")
        print(str(error))
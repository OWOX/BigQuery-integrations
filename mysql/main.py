from google.cloud import bigquery
from MySQLdb import connect, cursors
import os

# writeable part of the filesystem for Cloud Functions instance
gc_write_dir = "/tmp"

def get_file_mysql(mysql_configuration):
    """
        Querying data using Connector/Python via *host* MySQL server.
        The function return the full path to the file that has been downloaded.
    """
    # construct MySQLConnection object and query table on a server
    try:
        cnx = connect(user = mysql_configuration["user"], passwd = mysql_configuration["psswd"], host = mysql_configuration["host"],
                      db = mysql_configuration["database"], port = mysql_configuration["port"],
                      cursorclass= cursors.DictCursor )
        cursor = cnx.cursor()
        cursor.execute(mysql_configuration["query"])
        results = cursor.fetchall()
        file_name = "mysql.txt"

        with open(file_name, "w") as output_file:
            for row in results:
                output_file.write(json.dumps(row, default = str) + "\n")

        file_location = gc_write_dir + "/" + file_name
        print("Query <" + mysql_configuration["query"] + "> has completed successfully.")
    finally:
        try:
            cursor.close()
            cnx.close()
        except:
            print("Connection has not been established.")
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
    job_config.source_format = "NEWLINE_DELIMITED_JSON"
    job_config.write_disposition = bq_configuration["write_disposition"]
    job_config.autodetect = True

    # upload the file to BigQuery table
    with open(path_to_file, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_ref, location = bq_configuration["location"], job_config = job_config)
    job.result()
    print("The Job " + job.job_id + " in status " + job.state + " for table " + bq_configuration["project_id"] + "." + bq_configuration["dataset_id"] + "." + bq_configuration["table_id"] + ".")

def mysql(request):
    """
        Function to execute.
    """
    try:
        # get POST data from Flask.request object
        request_json = request.get_json()
        mysql_configuration = request_json["mysql"]
        bq_configuration = request_json["bq"]

        if not mysql_configuration.get("query"):
            mysql_configuration["query"] = "SELECT * FROM " + mysql_configuration["table_id"]
        if not mysql_configuration.get("port"):
            mysql_configuration["port"] = 3306
        if not bq_configuration.get("location"):
            bq_configuration["location"] = "US"
        bq_configuration["write_disposition"] = "WRITE_TRUNCATE"

    except Exception as error:
        print("An error occured with POST request data.")
        print(str(error))
        raise SystemExit

    # go to writable directory
    os.chdir(gc_write_dir)

    # get the file from MySQL server
    try:
        mysql_file = get_file_mysql(mysql_configuration)
    except Exception as error:
        print("An error occured trying to get file from MySQL server.")
        print(str(error))
        raise SystemExit

    # upload the file to BigQuery
    try:
        give_file_gbq(mysql_file, bq_configuration)
    except Exception as error:
        print("An error occured trying to upload file to Google BigQuery.")
        print(str(error))

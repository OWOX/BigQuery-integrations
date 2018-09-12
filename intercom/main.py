from google.cloud import bigquery
import os, re
import json, requests


# writeable part of the filesystem for Cloud Functions instance
gc_write_dir = "/tmp"

def get_intercom_data(intercom_configuration, entity):

    """
        Geeting and transforming Intercom data using Intercom API: https://developers.intercom.com/intercom-api-reference/reference
    """

    # Build get request
    headers = {
        "Authorization": "Bearer " + intercom_configuration["accessToken"],
        "Accept": "application/json"
    }

    request = requests.get("https://api.intercom.io/" + entity, headers=headers).json()
    data = request.get(entity)

    # Getting all pages from request
    if request.get("pages"):
        while request.get("pages").get("next"):
            request = requests.get(request.get("pages").get("next"), headers=headers).json()
            data += request.get(entity)
            print(request.get("pages").get("next"))
    print("Total number of " + entity + " eq " + str(len(data)) + "\nRunning writing data to the file.")


    # write data in newline delimited JSON file
    if len(data) > 0:
        with open(entity + '.json', 'w') as outfile:
            for row in data:
                if "custom_attributes" in row:
                    """
                    If you would like to load data from Custom Fileds - remove next row and uncomment next 2 rows below
                    """
                    row.pop("custom_attributes")
                   # custom_attributes = row.get("custom_attributes")
                   # new_custom_attributes = { key.replace(' ', '_'): value for key, value in custom_attributes.items() }
                   # row["custom_attributes"] = new_custom_attributes

                outfile.write(json.dumps(row) + os.linesep)
        outfile.close()

    return entity + '.json'



def load_to_gbq(json_file, bq_configuration, entity):
    """
        Loading data to BigQuery using *bq_configuration* settings.
    """
    # construct Client object with the path to the table in which data will be stored
    client = bigquery.Client(project = bq_configuration["project_id"])
    dataset_ref = client.dataset(bq_configuration["dataset_id"])
    table_ref = dataset_ref.table(entity)

    # determine uploading options
    job_config = bigquery.LoadJobConfig()
    job_config.write_disposition = 'WRITE_TRUNCATE'
    job_config.max_bad_records = 1
    job_config.source_format = "NEWLINE_DELIMITED_JSON"

    # Specifing a schema for users anв contacts and using autodetect for other tables
    if entity != "users" and entity != "contacts":
        job_config.autodetect = True
    else:
        job_config.schema = [
            bigquery.SchemaField(name="type", field_type="STRING", mode="NULLABLE"),
            bigquery.SchemaField(name="id", field_type="STRING", mode="NULLABLE"),
            bigquery.SchemaField(name="user_id", field_type="STRING", mode="NULLABLE"),
            bigquery.SchemaField(name="anonymous", field_type="BOOLEAN", mode="NULLABLE"),
            bigquery.SchemaField(name="email", field_type="STRING", mode="NULLABLE"),
            bigquery.SchemaField(name="phone", field_type="STRING", mode="NULLABLE"),
            bigquery.SchemaField(name="name", field_type="STRING", mode="NULLABLE"),
            bigquery.SchemaField(name="pseudonym", field_type="STRING", mode="NULLABLE"),
            bigquery.SchemaField(name="avatar", field_type="RECORD", mode="NULLABLE", fields = [
                    bigquery.SchemaField(name="type", field_type="STRING", mode="NULLABLE"),
                    bigquery.SchemaField(name="image_url", field_type="STRING", mode="NULLABLE")
                ]
        ),
            bigquery.SchemaField(name="app_id", field_type="STRING", mode="NULLABLE"),
            bigquery.SchemaField(name="location_data", field_type="RECORD", mode="NULLABLE", fields = [
                    bigquery.SchemaField(name="type", field_type="STRING", mode="NULLABLE"),
                    bigquery.SchemaField(name="city_name", field_type="STRING", mode="NULLABLE"),
                    bigquery.SchemaField(name="continent_code", field_type="STRING", mode="NULLABLE"),
                    bigquery.SchemaField(name="country_code", field_type="STRING", mode="NULLABLE"),
                    bigquery.SchemaField(name="country_name", field_type="STRING", mode="NULLABLE"),
                    bigquery.SchemaField(name="latitude", field_type="FLOAT", mode="NULLABLE"),
                    bigquery.SchemaField(name="longitude", field_type="FLOAT", mode="NULLABLE"),
                    bigquery.SchemaField(name="postal_code", field_type="STRING", mode="NULLABLE"),
                    bigquery.SchemaField(name="region_name", field_type="STRING", mode="NULLABLE"),
                    bigquery.SchemaField(name="timezone", field_type="STRING", mode="NULLABLE")
                ]
        ),
            bigquery.SchemaField(name="last_request_at", field_type="TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField(name="last_seen_ip", field_type="STRING", mode="NULLABLE"),
            bigquery.SchemaField(name="created_at", field_type="TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField(mode="NULLABLE", name="remote_created_at", field_type="TIMESTAMP"),
            bigquery.SchemaField(name="signed_up_at", field_type="TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField(name="updated_at", field_type="TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField(name="session_count", field_type="INTEGER", mode="NULLABLE"),
            bigquery.SchemaField(mode="NULLABLE", name="unsubscribed_from_emails", field_type="BOOLEAN"),
            bigquery.SchemaField(mode="NULLABLE", name="marked_email_as_spam", field_type="BOOLEAN"),
            bigquery.SchemaField(mode="NULLABLE", name="has_hard_bounced", field_type="BOOLEAN"),
            bigquery.SchemaField(mode="NULLABLE", name="user_agent_data", field_type="STRING"),
            bigquery.SchemaField(mode="NULLABLE", name="referrer", field_type="STRING"),
            bigquery.SchemaField(mode="NULLABLE", name="utm_source", field_type="STRING"),
            bigquery.SchemaField(mode="NULLABLE", name="utm_medium", field_type="STRING"),
            bigquery.SchemaField(mode="NULLABLE", name="utm_campaign", field_type="STRING"),
            bigquery.SchemaField(mode="NULLABLE", name="utm_content", field_type="STRING"),
            bigquery.SchemaField(mode="NULLABLE", name="utm_term", field_type="STRING"),

            bigquery.SchemaField(mode="NULLABLE", name="companies", field_type="RECORD", fields = [
               bigquery.SchemaField(mode="NULLABLE", name="type", field_type="STRING"),
               bigquery.SchemaField(mode="REPEATED", name="companies", field_type="RECORD", fields = [
                    bigquery.SchemaField(mode="NULLABLE", name="name", field_type="STRING"),
                    bigquery.SchemaField(mode="NULLABLE", name="id", field_type="STRING"),
                    bigquery.SchemaField(mode="NULLABLE", name="company_id", field_type="STRING"),
                    bigquery.SchemaField(mode="NULLABLE", name="type", field_type="STRING")
                ]
            )
            ]
        ),
            bigquery.SchemaField(mode="REPEATED", name="social_profiles", field_type="RECORD", fields = [
                bigquery.SchemaField(mode="NULLABLE", name="type", field_type="STRING"),
                bigquery.SchemaField(mode="REPEATED", name="social_profiles", field_type="RECORD", fields = [
                      bigquery.SchemaField(mode="NULLABLE", name="url", field_type="STRING"),
                      bigquery.SchemaField(mode="NULLABLE", name="id", field_type="STRING"),
                      bigquery.SchemaField(mode="NULLABLE", name="name", field_type="STRING"),
                      bigquery.SchemaField(mode="NULLABLE", name="username", field_type="STRING"),
                      bigquery.SchemaField(mode="NULLABLE", name="type", field_type="STRING")
                    ])
                ]),

          bigquery.SchemaField(mode="NULLABLE", name="tags", field_type="RECORD", fields = [
              bigquery.SchemaField(mode="NULLABLE", name="type", field_type="STRING"),
              bigquery.SchemaField(mode="REPEATED", name="tags", field_type="RECORD", fields = [
                  bigquery.SchemaField(mode="NULLABLE", name="id", field_type="STRING"),
                  bigquery.SchemaField(mode="NULLABLE", name="name", field_type="STRING"),
                  bigquery.SchemaField(mode="NULLABLE", name="type", field_type="STRING")
                ]),
            ]
        ),

            bigquery.SchemaField(mode="NULLABLE", name="segments", field_type="RECORD", fields = [
                bigquery.SchemaField(mode="NULLABLE", name="type", field_type="STRING"),
                bigquery.SchemaField(mode="REPEATED", name="segments", field_type="RECORD", fields = [
                    bigquery.SchemaField(mode="NULLABLE", name="id", field_type="STRING"),
                    bigquery.SchemaField(mode="NULLABLE", name="type", field_type="STRING")
                    ]
                )
            ]
        )
    ]


    # upload the file to BigQuery table
    with open(json_file, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_ref, location = bq_configuration["location"], job_config = job_config)
    job.result()
    print("The Job " + job.job_id + " in status " + job.state + " for table " + bq_configuration["project_id"] + "." + bq_configuration["dataset_id"] + "." + entity + ".")
    
    source_file.close()
    os.remove(json_file)


def intercom(request):
    """
        Function to execute.
    """
    try:
        # get POST data from Flask.request object
        request_json = request.get_json()
        intercom_configuration = request_json["intercom"]
        bq_configuration = request_json["bq"]

        if not bq_configuration.get("location"):
            bq_configuration["location"] = "US"

    except Exception as error:
        print("An error occured with POST request data.")
        print(str(error))
        raise SystemExit

   
    # go to writable directory
    os.chdir(gc_write_dir)
    
    
    # getting data from intercom

    for entity in intercom_configuration["entities"]:
        try:
            json_file = get_intercom_data(intercom_configuration, entity)
        except Exception as error:
            print("An error occured trying to get data from intercom.")
            print(str(error))
            raise SystemExit
        
        
        # upload the file to BigQuery
        if os.path.isfile(json_file):
            try:
                load_to_gbq(json_file, bq_configuration, entity)
            except Exception as error:
                print("An error occured trying to upload file to Google BigQuery.")
                print(str(error))
                
    print("All tasks have been completed.")
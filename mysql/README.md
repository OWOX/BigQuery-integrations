# Google BigQuery Integration with MySQL - servers

This documentation is also available in [RU](https://github.com/OWOX/BigQuery-integrations/blob/master/mysql/README_RU.md).

## About this script

The **mysql-bq-integration** module lets you automatically upload files from regularly updated tables on MySQL servers to Google BigQuery using Google Cloud Functions.


## How it works

An HTTP POST request invokes a Cloud function that gets the file from the MySQL server and uploads it to a BigQuery table. 
If the table already exists in the selected dataset, it will be rewritten.


## Requirements

- A Google Cloud Platform project with an activated billing account;
- Read access to the data source;
- The *WRITER* access to the dataset and *Job User* roles for the Cloud Functions service account in the BigQuery project to which you are going to upload the table (see the [Access](https://github.com/OWOX/BigQuery-integrations/tree/master/mysql#access) part of this doc);
- An HTTP client for POST requests invoking the Cloud function.


## Setup

1. Go to [Google Cloud Platform Console](https://console.cloud.google.com/home/dashboard/) and authorize using a Google account, or sign up if you don’t have an account yet.
2. Go to the project with billing activated or [create a new billing account](https://cloud.google.com/billing/docs/how-to/manage-billing-account#create_a_new_billing_account) for the project that hasn’t one.
3. Go to [Cloud Functions](https://console.cloud.google.com/functions/) and click **CREATE FUNCTION**. *Important to note:* using Cloud Functions is billed according to [this pricing](https://cloud.google.com/functions/pricing).
4. Fill in these fields:

    **Name**: *mysql-bq-integration* или любое другое подходящее название;

    **Memory allocated**: *2Gb* or less depending on the file that is being processed;

    **Trigger**: *HTTP*;

    **Source code**: *Inline editor*;

    **Runtime**: *Python 3.X*.
5. Copy the contents of the **main.py** file to the inline editor, the *main.py* tab.
6. Copy the contents of the **requirements.txt** file to the inline editor, the *requirements.txt* tab.
7. As a **Function to execute**, state *mysql*. 
8. In the **Advanced options** set the **Timeout** to *540 seconds* or less depending on the file that is being processed.
9. Complete creating the Cloud Function by clicking **Create**. 

## Access

### MySQL

Acquire the username and password from the MySQL server with the read access, where the database with the table is located.

### BigQuery

If the created Cloud Function and the BigQuery project are located in the same [Google Cloud Platform Console](https://console.cloud.google.com/home/dashboard/) project, then you don’t need to take any additional actions.

If they are located in different projects, then:
1. Go to [Cloud Functions](https://console.cloud.google.com/functions/) and click on the function you created to open the **Function details**.
2. On the **General** tab, find the **Service account** field and copy the email from there.
3. In Google Cloud Platform, go to **IAM & admin** - [IAM](https://console.cloud.google.com/iam-admin/iam) and select the project where you are going to upload the BigQuery table to.
4. Click the **+Add** - button above to add a new member. Paste the service account email to the **New members** field and select the *Job User*. Click **Save**.
5. Go to your BigQuery dataset and share one with the service account email. You need to [grant](https://cloud.google.com/bigquery/docs/datasets#controlling_access_to_a_dataset) *WRITER* access to the dataset. 

### Query

The data you need to upload to a BigQuery table will be acquired with a MySQL query.

The file schema is automatically defined in BigQuery. 

For the DATE data type to be defined correctly, the values of the field must use the “-” delimiter and have the “YYYY-MM-DD” format.

For the TIMESTAMP data type to be defined correctly, the values of the field must use the “-” delimiter for the date and the “:” delimiter for time. The format must be “YYYY-MM-DD hh:mm:ss”. Here’s the
[list of possible timestamp formats](https://cloud.google.com/bigquery/docs/schema-detect#timestamps).

## Usage

1. Go to [Cloud Functions](https://console.cloud.google.com/functions/) and click on the function you’ve created to open the **Function details**.
2. On the **Trigger** tab, copy the *URL address*. 
3. Using an HTTP client, send a POST request to this URL address. The request body must be in the JSON format:
```
{
  "mysql": 
        {
            "user": "mysql.user",
            "psswd": "mysql.password",
            "host": "host_name",
            "port": 3306,
            "database": "database_name",
            "table_id": "table_name",
            "query": "SELECT * FROM table_name"
        },
  "bq": 
        {
            "project_id": "my_bq_projec",
            "dataset_id": "my_bq_dataset",
            "table_id": "my_bq_table"
        }
}
```

| Property name | Object | Description |
| --- | --- | --- |
| Required properties |   
| user | mysql |  Name of the user on the FTPS server, who has the read access. |
| psswd | mysql | User password on the FTPS server. |
| host | mysql | MySQL server host. |
| database | mysql | Database on the MySQL server. |
| table_id | mysql | Table name in the database. This table will be queried. The property is required if the optional property “query” is not specified. |
| project_id | bq | Name of the BigQuery project where the table will be uploaded to. The project may be different from the one where the Cloud Function was created in. |
| dataset_id | bq | Name of the BigQuery dataset where the table will be uploaded to. |
| table_id | bq | Name of the BigQuery table where the file from the MySql server will be uploaded to. |
| Optional properties |
| query | mysql | A query that returns data you need to upload to the BigQuery table. The query must be sent to the table specified in the “database” dimension. If the “query” dimension is not specified, the query will be sent to the whole “table_id” table. |
| port | mysql | TCP/IP port of the MySQL server. Default: 3306. |
| location | bq | Geographical location of the table. Default: “US”. |

## Troubleshooting

Each Cloud Function invocation is being logged. You can view the logs in Google Cloud Platform:

1. Go to [Cloud Functions](https://console.cloud.google.com/functions/) and click on the function you created to open the **Function details**.
2. Click **View logs** in the top bar and see the latest logs at the levels *Error* and *Critical*.

Usually, these errors are caused by the issues with accessing the MySQL server, the BigQuery access, or errors in the imported file.

## Limitations

1. The size of the file processed must be no greater than 2Gb.
2. The Cloud Function invocation timeout must be no greater than 540 seconds.


## Sample usage

### Linux 

Invoke the function via the Linux terminal:

```
curl -X POST https://REGION-PROJECT_ID.cloudfunctions.net/mysql/ -H "Content-Type:application/json"  -d 
    '{
      "mysql": 
            {
                "user": "mysql.user",
                "psswd": "mysql.password",
                "host": "host_name",
                "port": 3306,
                "database": "database_name",
                "table_id": "table_name",
                "query": "SELECT * FROM table_name"
            },
      "bq": 
            {
                "project_id": "my_bq_projec",
                "dataset_id": "my_bq_dataset",
                "table_id": "my_bq_table"
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

trigger_url = "https://REGION-PROJECT_ID.cloudfunctions.net/mysql/"

headers = {"Content-Type": "application/json; charset=UTF-8"}
payload = {
            "mysql": 
                    {
                        "user": "mysql.user",
                        "psswd": "mysql.password",
                        "host": "host_name",
                        "port": 3306,
                        "database": "database_name",
                        "table_id": "table_name",
                        "query": "SELECT * FROM table_name"
                    },
            "bq": 
                    {
                        "project_id": "my_bq_projec",
                        "dataset_id": "my_bq_dataset",
                        "table_id": "my_bq_table"
                    }
}
Http().request(method = "POST", uri = trigger_url, body = json.dumps(payload), headers = headers)
```

### [Google Apps Script](https://developers.google.com/apps-script/)

Paste this code with your parameters and launch the function:

```
function runmysql() {
  trigger_url = "https://REGION-PROJECT_ID.cloudfunctions.net/mysql/"
  var payload = {
                  "mysql": 
                        {
                            "user": "mysql.user",
                            "psswd": "mysql.password",
                            "host": "host_name",
                            "port": 3306,
                            "database": "database_name",
                            "table_id": "table_name",
                            "query": "SELECT * FROM table_name"
                        },
                  "bq": 
                        {
                            "project_id": "my_bq_projec",
                            "dataset_id": "my_bq_dataset",
                            "table_id": "my_bq_table"
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

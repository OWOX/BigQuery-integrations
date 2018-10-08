# Google BigQuery Integration with HTTPS - servers

This documantation is also available in [RU](https://github.com/OWOX/BigQuery-integrations/tree/master/https/README_RU.md).

## About this script

The **https-bq-integration** module lets you automatically upload data from the regularly updated file on an HTTPS server 
to Google BigQuery using Google Cloud Functions.


## How it works

An HTTP POST request invokes a Cloud function that gets the file from the HTTPS server and uploads it to a BigQuery table. 
If the table already exists in the selected dataset, it will be rewritten.


## Requirements

- A Google Cloud Platform project with an activated billing account;
- Access to the file by an http(s) link;
- The *BigQuery Data Editor* and *Job User* roles for the Cloud Functions service account in the BigQuery project to which you are going to upload the table (see the [Access](https://github.com/OWOX/BigQuery-integrations/tree/master/https/README_RU.md#access) part of this doc);
- An HTTP client for POST requests invoking the Cloud function


## Setup

1. Go to [Google Cloud Platform Console](https://console.cloud.google.com/home/dashboard/) and authorize using a Google account, or sign up if you don’t have an account yet.
2. Go to the project with billing activated or [create a new billing account](https://cloud.google.com/billing/docs/how-to/manage-billing-account#create_a_new_billing_account) for the project that hasn’t one.
3. Go to [Cloud Functions](https://console.cloud.google.com/functions/) and click **CREATE FUNCTION**. *Important to note:* using Cloud Functions is billed according to [this pricing](https://cloud.google.com/functions/pricing).
4. Fill in these fields:

    **Name**: *https-bq-integration* or any other name you see fit;

    **Memory allocated**: *2Gb* or less depending on the file that is being processed;

    **Trigger**: *HTTP*;

    **Source code**: *Inline editor*;

    **Runtime**: *Python 3.X*.
5. Copy the contents of the **main.py** file to the inline editor, the *main.py* tab.
6. Copy the contents of the **requirements.txt** file to the inline editor, the *requirements.txt* tab.
7. As a **Function to execute**, state *https*. 
8. In the **Advanced options** set the **Timeout** to *540 seconds* or less depending on the file that is being processed.
9. Complete creating the Cloud Function by clicking **Create**. 

## Access

### HTTPS

The file you need to upload to a BigQuery table must be available by an http(s) link.

### BigQuery

If the created Cloud Function and the BigQuery project are located in the same [Google Cloud Platform Console](https://console.cloud.google.com/home/dashboard/) project, then you don’t need to take any additional actions.

If they are located in different projects, then:
1. Go to [Cloud Functions](https://console.cloud.google.com/functions/) and click on the function you created to open the **Function details**.
2. On the **General** tab, find the **Service account** field and copy the email from there.
3. In Google Cloud Platform, go to **IAM & admin** - [IAM](https://console.cloud.google.com/iam-admin/iam) and select the project where you are going to upload the BigQuery table to.
4. Click the **+Add** - button above to add a new member. Paste the service account email to the **New members** field and select the roles as *BigQuery Data Editor* and *Job User*. Click **Save**.

## File

The file you need to acquire from the HTTPS server can have any appropriate extension: .json, .txt, .csv. However, it must be in the JSON (newline-delimited) or CSV (Comma-separated values) format.

The file schema is automatically defined in BigQuery. 

For the DATE data type to be defined correctly, the values of the field must use the “-” delimiter and have the “YYYY-MM-DD” format.

For the TIMESTAMP data type to be defined correctly, the values of the field must use the “-” delimiter for the date and the “:” delimiter for time. The format must be “YYYY-MM-DD hh:mm:ss”. Here’s the
([list of possible timestamp formats](https://cloud.google.com/bigquery/docs/schema-detect#timestamps)).

### JSON (newline-delimited)

The JSON file contents must look as follows:
```
{"column1": "my_product" , "column2": 40.0}
{"column1": , "column2": 54.0}
…
```
### CSV

The CSV file contents must look as follows:
```
column1,column2
my_product,40.0
,54.0
…
```
For the table scheme to be defined correctly, the first line of the CSV file — the header — must contain only the STRING values. 
In the rest of the lines, at least one column must contain numerical values.

## Usage

1. Go to [Cloud Functions](https://console.cloud.google.com/functions/) and click on the function you’ve created to open the **Function details**.
2. On the **Trigger** tab, copy the *URL address*. 
3. Using an HTTP client, send a POST request to this URL address. The request body must be in the JSON format:
```
{
   "https": {
                "path_to_file": "https://server_host/path/to/file/",
                "user": "https.user_name",
                "psswd": "https.password"
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

| Property name | Object | Description |
| --- | --- | --- |
| Required properties |   
| user | https| Name of the user on the HTTPS server, who has the read access. |
| psswd | https | User password on the HTTPS server. |
| path_to_file | https | Full path to the file on the HTTPS server. It always must look like this: “https://host/path/to/file/” |
| project_id | bq | Name of the BigQuery project where the table will be uploaded to. The project may be different from the one where the Cloud Function was created in. |
| dataset_id | bq | Name of the BigQuery dataset where the table will be uploaded to. |
| table_id | bq | Name of the BigQuery table where the file from the HTTPS server will be uploaded to. |
| delimiter | bq | Field delimiter in the CSV file. The property is required if you choose CSV as source_format. Supported delimiters are: “,”, “|”, and ”\t”. |
| source_format | bq | The format of the file uploaded to BigQuery. Supported formats: “NEWLINE_DELIMITED_JSON", “CSV”. |
| Optional properties |
| location | bq | Geographical location of the table. Default: “US”. |

## Troubleshooting

Each Cloud Function invocation is being logged. You can view the logs in Google Cloud Platform:

1. Go to [Cloud Functions](https://console.cloud.google.com/functions/) and click on the function you created to open the **Function details**.
2. Click **View logs** in the top bar and see the latest logs at the levels *Error* and *Critical*.

Usually, these errors are caused by the issues with accessing the FTPS server, the BigQuery access, or errors in the imported file.

## Limitations

1. The size of the file processed must be no greater than 2Gb.
2. The Cloud Function invocation timeout must be no greater than 540 seconds.


## Sample usage

### Linux 

Invoke the function via the Linux terminal:

```
curl -X POST https://REGION-PROJECT_ID.cloudfunctions.net/https/ -H "Content-Type:application/json"  -d 
    '{
        "https": 
                {
                    "path_to_file": "https://server_host/path/to/file/",
                    "user": "https.user_name",
                    "psswd": "https.password"
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

trigger_url = "https://REGION-PROJECT_ID.cloudfunctions.net/https/"
headers = { "Content-Type": "application/json" }
payload = {
                "https": 
                        {
                            "path_to_file": "https://server_host/path/to/file/",
                            "user": "https.user_name",
                            "psswd": "https.password"
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

Paste this code with your parameters and launch the function:

```
function runhttps() {
  trigger_url = "https://REGION-PROJECT_ID.cloudfunctions.net/https/"
  var payload = {
                    "https": 
                            {
                                "path_to_file": "https://server_host/path/to/file/",
                                "user": "https.user_name",
                                "psswd": "https.password"
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

# Google BigQuery Integration with [Intercom](https://www.intercom.com/)

## About this script

The **intercom-bq-integration**  module lets you automatically upload data from Intercom to Google BigQuery using Google Cloud Functions. 
Currently, the module can import these entities: *users*, *companies*, *contacts*, *admins*, *conversations*, *teams*, *tags*, *segments*. 
By default, the module doesn’t support *custom attributes*, yet it’s easy to fix. To enable *custom attributes*, add to the import schema the names and data type of the custom fields, then delete the line *row.pop("custom_attributes")* from the script.


## How it works

An HTTP POST request invokes a Cloud Function which gets data from Intercom via the [Intercom API](An HTTP POST request invokes a Cloud Function which gets data from Intercom via the [Intercom API](https://developers.intercom.com/intercom-api-reference/reference). 
Then, uploads it to the corresponding Google BigQuery tables. If the table in the chosen dataset already exists, it will be rewritten.

## Requirements

- A Google Cloud Platform project with an activated billing account;
- Access to Intercom with the ability to create Apps;
- Access to edit and create jobs in Google BigQuery (roles *BigQuery Data Editor* and *BigQuery Job User*) for the Cloud Functions service account in the BigQuery project you want to upload the table to (see the [Access](https://github.com/OWOX/BigQuery-integrations/tree/master/intercom#Access) part);
- An HTTP client for POST requests invoking the Cloud function

## Setup

1. Go to [Google Cloud Platform Console](https://console.cloud.google.com/home/dashboard/) and authorize using a Google account, or sign up if you don’t have an account yet.
2. Go to the project with billing activated or [create a new billing account](https://cloud.google.com/billing/docs/how-to/manage-billing-account#create_a_new_billing_account) for the project that hasn’t one.
3. Go to [Cloud Functions](https://console.cloud.google.com/functions/) and click **CREATE FUNCTION**. *Important to note:* using Cloud Functions is billed according to [this pricing](https://cloud.google.com/functions/pricing).
4. Fill in these fields:

    **Name**: *intercom-bq-integration* or any other name you see fit;

    **Memory allocated**: *2Gb* or less depending on the file that is being processed;

    **Trigger**: *HTTP*;

    **Source code**: *Inline editor*;

    **Runtime**: *Python 3.X*.
5. Copy the contents of the **main.py** file to the inline editor, the *main.py* tab.
6. Copy the contents of the **requirements.txt** file to the inline editor, the *requirements.txt* tab.
7. As a **Function to execute**, state *intercom*. 
8. In the **Advanced options** set the **Timeout** to *540 seconds* or less depending on the file that is being processed.
9. Complete creating the Cloud Function by clicking **Create**. 

## Access

### Intercom

In Intercom, get Access Token with the read access to any data. To do this, go to **Settings** > **Developers** > **Create an App**. Provide permissions to read any data by checking the corresponding boxes. Once the app is created, copy and save the Access Token.

### BigQuery

If the created Cloud Function and the BigQuery project are located in the same [Google Cloud Platform Console](https://console.cloud.google.com/home/dashboard/) project, then you don’t need to take any additional actions.

If they are located in different projects, then:
1. Go to [Cloud Functions](https://console.cloud.google.com/functions/) and click on the function you created to open the **Function details**.
2. On the **General** tab, find the **Service account** field and copy the email from there.
3. In Google Cloud Platform, go to **IAM & admin** - [IAM](https://console.cloud.google.com/iam-admin/iam) and select the project where you are going to upload the BigQuery table to.
4. Click the **+Add** - button above to add a new member. Paste the service account email to the **New members** field and select the roles as *BigQuery Data Editor* and *Job User*. Click **Save**.

## Usage

1. Go to [Cloud Functions](https://console.cloud.google.com/functions/) and click on the function you’ve created to open the **Function details**.
2. On the **Trigger** tab, copy the *URL address*. 
3. Using an HTTP client, send a POST request to this URL address. The request body must be in the JSON format:
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

| Property name | Object | Description |
| --- | --- | --- |
| Required properties |   
| accessToken | intercom |  Your Access Token to the Intercom API. |
| psswd | intercom | The list of the Intercom entities which data you want to import to BigQuery. In the sample, we’ve listed all values possible. |
| project_id | bq | Name of the BigQuery project where the table will be downloaded to. The project may be different from the one where the Cloud Function was created in. |
| dataset_id | bq | Name of the BigQuery dataset where the table will be uploaded to. |
| table_id | bq | Name of the BigQuery table where the file from the MySql server will be uploaded to. |
| Optional properties |
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
from urllib import urlencode
from httplib2 import Http

trigger_url = "https://REGION-PROJECT_ID.cloudfunctions.net/intercom/"
headers = { "Content-Type": "application/json" }
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
Http().request(trigger_url, "POST", urlencode(payload), headers = headers)
```

### [Google Apps Script](https://developers.google.com/apps-script/)

Paste this code with your parameters and launch the function:


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
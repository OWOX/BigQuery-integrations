# DEPRECATED AND NOT MAINTAINED

# BigQuery-integrations
Import files (data) from Intercom, FTP(S), SFTP, MySQL, etc. servers into BigQuery.

This documentation is also available in [RU](https://github.com/OWOX/BigQuery-integrations/blob/master/README_RU.md). 

## What is BigQuery-integrations

BigQuery-integrations is a set of Python scripts that let you automate data import to [Google BigQuery](https://cloud.google.com/bigquery/) using [Google Cloud Functions](https://cloud.google.com/functions/). 

The current version of BigQuery-integrations features scripts for importing from:

- [amoCRM](https://github.com/OWOX/BigQuery-integrations/tree/master/amocrm);
- [FTP](https://github.com/OWOX/BigQuery-integrations/tree/master/ftp);
- [FTPS](https://github.com/OWOX/BigQuery-integrations/tree/master/ftps);
- [HTTP(s)](https://github.com/OWOX/BigQuery-integrations/tree/master/https);
- [Intercom](https://github.com/OWOX/BigQuery-integrations/tree/master/intercom);
- [ExpertSender](https://github.com/OWOX/BigQuery-integrations/tree/master/expertsender);
- [MySQL](https://github.com/OWOX/BigQuery-integrations/tree/master/mysql);
- [SFTP](https://github.com/OWOX/BigQuery-integrations/tree/master/sftp).


## How it works

An HTTP POST request invokes a Cloud function that gets the file from the server and uploads it to a BigQuery table. 
If the table already exists in the selected dataset, it will be rewritten.

## Requirements

To launch any of these scripts, you need:
- A Google Cloud Platform project with an activated billing account;
- Read access to the data source;
- The *WRITER* access to the dataset and *Job User* roles for the Cloud functions service account in the BigQuery project to which you are going to upload the table;
- An HTTP client for POST requests invoking the Cloud function.

## Setup and usage

To launch the scripts, follow the steps described in the readme files in the function folder. 
You don’t need to edit the functions’ code.
The detailed documentation for each function is by the links below:

- [amoCRM (RU)](https://github.com/OWOX/BigQuery-integrations/tree/master/amocrm/README_RU.md);
- [FTP](https://github.com/OWOX/BigQuery-integrations/tree/master/ftp/README.md);
- [FTPS](https://github.com/OWOX/BigQuery-integrations/tree/master/ftps/README.md);
- [HTTP(s)](https://github.com/OWOX/BigQuery-integrations/tree/master/https/README.md);
- [Intercom](https://github.com/OWOX/BigQuery-integrations/tree/master/intercom/README.md);
- [ExpertSender (RU)](https://github.com/OWOX/BigQuery-integrations/tree/master/expertsender/README_RU.md);
- [MySQL](https://github.com/OWOX/BigQuery-integrations/tree/master/mysql/README.md);
- [SFTP](https://github.com/OWOX/BigQuery-integrations/tree/master/sftp/README.md).


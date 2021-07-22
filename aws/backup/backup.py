"""
Lambda function for RDS snapshots
Author: Andrew Jarombek
Date: 6/8/2019
"""

import os
import boto3
import json
import gzip
from botocore.client import Config
import subprocess


def create_backup(event, context):
    """
    Create a backup of an RDS MySQL database and store it on S3
    :param event: provides information about the triggering of the function
    :param context: provides information about the execution environment
    :return: True when successful
    """

    # Set the path to the executable scripts in the AWS Lambda environment.
    # Source:
    # https://aws.amazon.com/blogs/compute/running-executables-in-aws-lambda/
    os.environ['PATH'] = (os.environ['PATH'] + ":" +
                          os.environ['LAMBDA_TASK_ROOT'])

    # Get the DB_HOST environment variable from the lambda function
    host = os.environ['DB_HOST']
    bucket = os.environ['BUCKET']

    # Use Secrets Manager to get RDS username and password
    secretsmanager = boto3.client('secretsmanager', 'us-east-2')
    response = secretsmanager.get_secret_value(SecretId='umphbase-secret')
    secret_string = response.get("SecretString")
    secret_dict = json.loads(secret_string)
    username = secret_dict.get('username')
    password = secret_dict.get('password')

    # To execute the bash script on AWS Lambda, change its permissions and move
    # it into the /tmp/ directory.
    # Source: https://stackoverflow.com/a/48196444
    subprocess.check_call(["cp ./backup.sh /tmp/backup.sh"], shell=True)
    subprocess.check_call(["chmod 755 /tmp/backup.sh"], shell=True)
    subprocess.check_call(["/tmp/backup.sh", "prod", host, username, password])

    # Use gzip utility to compress the snapshot.
    with open('/tmp/umphbase.sql', 'rb') as sql_file:
        with gzip.open('/tmp/umphbase.sql.gz', 'wb') as gz_file:
            gz_file.writelines(sql_file)

    # By default, S3 resolves buckets using the internet.  To use the VPC
    # endpoint instead, use the 'path' addressing style config.
    # Source: https://stackoverflow.com/a/44478894
    s3 = boto3.resource(service_name='s3',
                        region_name='us-east-2',
                        config=Config(s3={'addressing_style': 'path'}))

    # Make sure to give READ permission to everyone with every upload.
    public_uri = "http://acs.amazonaws.com/groups/global/AllUsers"
    s3.meta.client.upload_file(Filename='/tmp/umphbase.sql.gz',
                               Bucket=bucket,
                               Key='umphbase.sql.gz',
                               ExtraArgs={'GrantRead': 'uri=%s' % public_uri})

    return True

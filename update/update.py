import os
import boto3
import json
import subprocess
from botocore.client import Config


def update_database(event, context):
    """
    Update an RDS MySQL database with newest ATU setlists
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

    # Use Secrets Manager to get RDS username and password
    secretsmanager = boto3.client('secretsmanager', 'us-east-2')
    response = secretsmanager.get_secret_value(SecretId='umphbase/rds-secret')
    secret_string = response.get("SecretString")
    secret_dict = json.loads(secret_string)
    username = secret_dict.get('username')
    password = secret_dict.get('password')

    # # By default, S3 resolves buckets using the internet.  To use the VPC
    # # endpoint instead, use the 'path' addressing style config.
    # # Source: https://stackoverflow.com/a/44478894
    # s3 = boto3.client(service_name='s3')
    # s3.download_file(Bucket='lambda-function-python-packages',
    #                  Key='UpdateUmphbase.zip',
    #                  Filename='/tmp/package.zip')

    # To execute the bash script on AWS Lambda, change its permissions and move
    # it into the /tmp/ directory.
    # Source: https://stackoverflow.com/a/48196444
    def make_available(file):
        subprocess.check_call(["cp ./%s /tmp/%s" % (file, file)], shell=True)
        subprocess.check_call(["chmod 755 /tmp/%s" % (file)], shell=True)

    make_available("update.sh")
    make_available("pull.py")
    make_available("sql_push.py")

    # TODO: Why do we need this? We might not...
    subprocess.check_call(["cp ./update.sh /tmp/update.sh"], shell=True)
    subprocess.check_call(["chmod 755 /tmp/update.sh"], shell=True)

    # TODO: Figure out how to abstract this to here.
    # path = '/tmp/atu_database'
    subprocess.check_call(["/tmp/update.sh", host, username, password])

    return True

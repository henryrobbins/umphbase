import os
import boto3
import json
import update
from sql_util import Credentials


CHARSET = "UTF-8"


def main(event, context):
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

    # TODO: No longer hard code the AWS Region
    # Use Secrets Manager to get RDS username and password
    secretsmanager = boto3.client('secretsmanager', 'us-east-2')
    response = secretsmanager.get_secret_value(SecretId='umphbase-secret')
    secret_string = response.get("SecretString")
    secret_dict = json.loads(secret_string)
    username = secret_dict.get('username')
    password = secret_dict.get('password')

    # Look to ATU for changes and update the RDS SQL database
    credentials = Credentials(host=host,
                              database="umphbase",
                              user=username,
                              password=password)
    log = update.main(credentials)

    # Send an email with logging information
    body = (
    "All Things Umphrey's: https://allthings.umphreys.com/setlists/ \n\n"
    "Log from Update Lambda Function call: \n\n"
    "%s" % log
    )

    email = os.environ['EMAIL']
    client = boto3.client('ses', region_name='us-east-2')
    response = client.send_email(
        Destination={
            'ToAddresses': [email],
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': CHARSET,
                    'Data': body,
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': "[UMPHBASE] Update Lambda Function",
            },
        },
        Source=email,
    )

    # Trigger the Backup Lambda Function
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(FunctionName=os.environ['BACKUP'],
                         InvocationType='Event')

    return True

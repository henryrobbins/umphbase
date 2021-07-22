import os
import boto3
import json
import pull
import sql_push


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
    response = secretsmanager.get_secret_value(SecretId='umphbase-secret')
    secret_string = response.get("SecretString")
    secret_dict = json.loads(secret_string)
    username = secret_dict.get('username')
    password = secret_dict.get('password')

    # Pull from ATU and push to RDS SQL database
    path = '/tmp/atu_database'
    pull.main(path)
    sql_push.main(path, 'arguments', host, 'umphbase', username, password)

    return True

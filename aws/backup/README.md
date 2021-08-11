# Backup Lambda Function

*Relies on multiple resources defined in the
[Umphbase CloudFormation Stack](../README.md)*

This [AWS Lambda](https://aws.amazon.com/lambda/) function is responsible for
creating a snapshot of a MySQL [RDS Database](https://aws.amazon.com/rds/) and
uploading it to [S3](https://aws.amazon.com/s3/) where it is made publicly
available via an endpoint.

## Deploy & Invoke

A [Makefile](Makefile) is provided with targets for deploying and invoking the
Lambda Function. The available targets are described in the table below.

| Target        | Description                                               |
| ------------- | --------------------------------------------------------- |
| deploy        | Update the source code of the Lambda Function             |
| invoke        | Invoke the Lambda Function                                |
| zip           | Create a zip directory with lambda function source code   |
| upload        | Upload the zip directory to the deployment S3 Bucket      |
| update        | Update the Lambda Function from the S3 Bucket             |
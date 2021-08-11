# Update Lambda Function

*Relies on multiple resources defined in the
[Umphbase CloudFormation Stack](../README.md)*

This [Lambda Function](https://aws.amazon.com/lambda/) is responsible for
pulling the newest data from
[All Things Umphrey's](https://allthings.umphreys.com/) (ATU) and updating a
MySQL [RDS Database](https://aws.amazon.com/rds/). As the function has multiple
dependencies, it utilizes a [Lambda Layer](../layer/README.md).

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

# Backupmphbase

This [AWS Lambda](https://aws.amazon.com/lambda/) function is responsible for
creating a snapshot of a MySQL [RDS Database](https://aws.amazon.com/rds/) and
uploading it to [S3](https://aws.amazon.com/s3/) where it is made publicly
available via an endpoint.

## Build & Deploy

*NOTE: This assume the BackupUmphbase function has already been created
properly, the RDS database is setup, Secrets Manager has the username and
password for this RDS database, and the S3 bucket is created.*

A [Makefile](Makefile) is provided with targets for building and deploying the
the Lambda function. To build and deploy, run the following commands:

```
make lambda
make deploy
```

The table below provides descriptions of all available targets.

| Target        | Description                                               |
| ------------- | --------------------------------------------------------- |
| lambda        | Create a zip directory with lambda function source code   |
| deploy        | Deploy lambda function                                    |
| invoke        | Invoke the lambda function                                |


## License

Licensed under the [GPL-3.0 License](https://choosealicense.com/licenses/gpl-3.0/)

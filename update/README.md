# UpdateUmphbase

This [AWS Lambda](https://aws.amazon.com/lambda/) function is responsible for
pulling data from [All Things Umphrey's](https://allthings.umphreys.com/) (ATU)
and updating a MySQL [RDS Database](https://aws.amazon.com/rds/). As the
function has multiple dependencies, it utilizes a
[Lambda Layer](https://docs.aws.amazon.com/lambda/latest/dg/invocation-layers.html).

## Build & Deploy

*NOTE: This assume the UpdateUmphbase function has already been created
properly, the RDS database is setup, and Secrets Manager has the username and
password for this RDS database.*

A [Makefile](Makefile) is provided with targets for building and deploying both
the Lambda function and layer. To build and deploy, run the following commands:

```
make all
make deploy
```

The table below provides descriptions of all available targets.

| Target        | Description                                               |
| ------------- | --------------------------------------------------------- |
| all           | Create zip directories for both lambda function and layer |
| layer         | Create a zip directory with lambda layer source code      |
| lambda        | Create a zip directory with lambda function source code   |
| deploy        | Deploy both the lambda function and layer                 |
| deploy-layer  | Deploy lambda layer and update lambda function layers     |
| deploy-lambda | Deploy lambda function                                    |
| invoke        | Invoke the lambda function                                |


## License

Licensed under the [GPL-3.0 License](https://choosealicense.com/licenses/gpl-3.0/)

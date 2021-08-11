# Umphbase CloudFormation Stack

One of the services offered by Amazon Web Services (AWS) is
[CloudFormation](https://aws.amazon.com/cloudformation/). CloudFormation
allows one "to model a collection of AWS resources." This is done through a
"template [which] describes [these] resources and their dependencies." This
service is utilized to create the Umphbase stack which is responsible for
doing daily updates of umphbase and backing up the database to a public
endpoint.

The [template.yaml](template.yaml) file is used to create the stack. This
template defines the following resources.

| Resource  | Type                   | Description                              |
| --------- | ---------------------- | ---------------------------------------- |
| RootRole  | IAM::Role              | Provides permissions to Lambda Functions |
| Secret    | SecretsManager::Secret | Stores database access credentials       |
| Umphbase  | RDS::DBInstance        | Database for storing setlist information |
| Bucket    | S3::Bucket             | Manages public endpoint for backup       |
| Layer     | Lambda::LayerVersion   | Stores necessary Python dependencies     |
| Update    | Lambda::Function       | Used to update the database              |
| Backup    | Lambda::Function       | Used to backup the database              |

Creating the Umphbase stack requires creating an [S3](https://aws.amazon.com/s3/)
bucket with the Lambda Function and Layer source code. The [update](update)
and [backup](backup) directories contain the source code for each Lambda
Function respectively. The [layer](layer) directory contains the source code
for the Lambda Layer.

To make the deployment bucket, first edit the [.env](.env)
file to choose a different bucket name; S3 Buckets in AWS must have unique names
and the default values are already in use. It is left as an exercise for the
reader to determine who is using them ;).

```
#.env
DEPLOYMENT_BUCKET=[something-else]
```

Then, use the make target `bucket` to make the bucket and populate it with the
source code for the Lambda Functions and Lambda Layer. After the bucket has been
created, use the target `create-stack` for creating the Umphbase stack.

```
make bucket
make create-stack
```

It is recommended to change the default database password of `password`. You
can either edit the [.env](.env) file

```
#.env
DB_PASSWORD=[your_password]
```

or pass in the environment variable when you create the stack

```
make create-stack DB_PASSWORD=[your_password]
```

Alternatively, you can create the stack using
[AWS Management Console](https://aws.amazon.com/console/) or
[AWS Command Line Interface (CLI)](https://aws.amazon.com/cli/).

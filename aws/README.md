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

*Note: The [update](update) and [backup](backup) directories contain the source
code for each Lambda Function respectively. The [layer](layer) directory
contains the source code for the Lambda Layer.*

The template for the CloudFormation stack requires multiple parameters which
are defined in the `.env` file. The [.env.example](.env.example) file provides
an example setup. The `UMPHBASE_BUCKET` and `DEPLOYMENT_BUCKET` environment
variables define the names of the two [S3](https://aws.amazon.com/s3/) buckets
where the backup and Lambda Function source code is stored respectively. These
values *must* be changed as S3 Buckets in AWS must have globally unique names
and the default values are already in use. It is left as an exercise for the
reader to determine who is using them ;).

```
#.env.example -> .env
UMPHBASE_BUCKET=[something-else]
DEPLOYMENT_BUCKET=[something-else]
```

Other environment variables can be changed as well. Two recommended changes are
to choose a new password and to choose an email to receive logging information
when the Lambda Functions are run.

```
#.env.example -> .env
DB_PASSWORD=[your_password]
EMAIL=[your@email.com]
```

If an email is provided, the `email` make target can be used to verify the
email address. An email will be sent to the email address defined in the `.env`
file which provides a link to finish the verification.

Next, use the make target `bucket` to make the deployment bucket and populate
it with the source code for the Lambda Functions and Lambda Layer. After the
bucket has been created, use the target `create-stack` for creating the
Umphbase stack.

```
make bucket
make create-stack
```

Alternatively, you can create the stack using
[AWS Management Console](https://aws.amazon.com/console/) or
[AWS Command Line Interface (CLI)](https://aws.amazon.com/cli/).

Lastly, the Update Lambda Function will only add the most recent shows to the
database. To initialize the AWS RDS database with the entire setlist history,
use the target `init`.

```
make init
```

# Umphbase AWS CloudFormation Stack

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
| RootRole  | IAM::Role              | Provides permissions to lambda functions |
| Secret    | SecretsManager::Secret | Stores database access credentials       |
| Umphbase  | RDS::DBInstance        | Database for storing setlist information |
| Bucket    | S3::Bucket             | Manages public endpoint for backup       |
| Layer     | Lambda::LayerVersion   | Stores necessary Python dependencies     |
| Update    | Lambda::Function       | Used to update the database              |
| Backup    | Lambda::Function       | Used to backup the database              |

Creating the Umphbase stack requires creating [S3](https://aws.amazon.com/s3/)
buckets with the lambda function and layer source code. The [update](update)
and [backup](backup) directories contain the source code for each lambda
function respectively. The layer source code is defined within the
[update](update) directory as this is the lambda function which requires it.
The [Makefile](Makefile) provides a target for creating these three buckets.

***Note:** If you wish to create and manage your own version of the Umphbase stack,
you will need to edit [Makefile](Makefile), [backup/Makefile](backup/Makefile),
and [update/Makefile](update/Makefile) and change the environment variables
`BACKUP_BUCKET`, `UPDATE_BUCKET`, and `LAYER_BUCKET`. This is because buckets
in AWS must have unique names and the defualt values are already in use. It is
left as an exercise for the reader to determine who is using them ;).*

```
make buckets
```

After the buckets have been created, the [Makefile](Makefile) also provides a
target for creating the Umphbase stack.

```
make cloudformation DB_PASSWORD=your_password
```

It is recommended to change the default database password of `password`. If you
use the make target, the database username will be `root`. Alternativley, you
can create the stack using
[AWS Management Console](https://aws.amazon.com/console/) or
[AWS Command Line Interface (CLI)](https://aws.amazon.com/cli/).

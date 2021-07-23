# TODO: just define these in one place
# Note: Database names must be globally unique
UMPHBASE_BUCKET=umphbase-bucket
BACKUP_BUCKET=umphbase-backup-source
UPDATE_BUCKET=umphbase-update-source
LAYER_BUCKET=umphbase-layer-bucket
DB_USERNAME?=root
DB_PASSWORD?=password
REGION=us-east-2

# Create the S3 bucket for the BackupUmphbase source code
backup-bucket:
	aws s3 mb s3://$(BACKUP_BUCKET) --region $(REGION)
	cd backup && make lambda
	cd backup && make deploy

# Create the S3 bucket for the BackupUmphbase source code
update-bucket:
	aws s3 mb s3://$(UPDATE_BUCKET) --region $(REGION)
	cd update && make lambda
	cd update && make deploy-lambda

# Create the S3 bucket for the layer
layer-bucket:
	aws s3 mb s3://$(LAYER_BUCKET) --region $(REGION)
	cd update && make layer
	aws s3api put-object --bucket $(LAYER_BUCKET) --key layer.zip \
	--body update/layer/layer.zip

# Create all S3 buckets
buckets: backup-bucket update-bucket layer-bucket

# Create CloudFormation
cloudformation:
	aws cloudformation create-stack \
	--stack-name Umphbase \
	--template-body file://template.yaml \
	--parameters \
	ParameterKey=BucketName,ParameterValue=$(UMPHBASE_BUCKET) \
	ParameterKey=LayerBucketName,ParameterValue=$(LAYER_BUCKET) \
	ParameterKey=UpdateBucketName,ParameterValue=$(UPDATE_BUCKET) \
	ParameterKey=BackupBucketName,ParameterValue=$(BACKUP_BUCKET) \
	ParameterKey=DBUsername,ParameterValue=$(DB_USERNAME) \
	ParameterKey=DBPassword,ParameterValue=$(DB_PASSWORD) \
	--capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM
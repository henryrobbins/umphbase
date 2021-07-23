# Set Make variables from .env file
include .env
export

# Create the S3 bucket for the Backup source code
backup-bucket:
	aws s3 mb s3://$(BACKUP_BUCKET) --region $(REGION)
	cd backup && make zip
	cd backup && make deploy

# Create the S3 bucket for the Update source code
update-bucket:
	aws s3 mb s3://$(UPDATE_BUCKET) --region $(REGION)
	cd update && make zip
	cd update && make deploy

# Create the S3 bucket for the layer
layer-bucket:
	aws s3 mb s3://$(LAYER_BUCKET) --region $(REGION)
	cd layer && make zip
	cd layer && make deploy

# Create all S3 buckets
buckets: backup-bucket update-bucket layer-bucket

# Template CloudFormation command
cloudformation:
	aws cloudformation $(COMMAND) \
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

# Create CloudFormation stack
create-stack:
	make cloudformation COMMAND=create-stack

# Update CloudFormation stack
update-stack:
	make cloudformation COMMAND=update-stack
# Set Make variables from .env file
include .env
export

# Deploy the Backup source code to the deployment S3 bucket
deploy-backup:
	cd backup && make zip
	cd backup && make deploy

# Deploy the Update source code to the deployment S3 bucket
deploy-update:
	cd update && make zip
	cd update && make deploy

# Deploy the Lambda layer source code to the deployment S3 bucket
deploy-layer:
	cd layer && make zip
	cd layer && make deploy

# Create the S3 bucket for umphbase deployment code
bucket:
	aws s3 mb s3://$(DEPLOYMENT_BUCKET) --region $(REGION)
	make deploy-backup
	make deploy-update
	make deploy-layer

# Template CloudFormation command
cloudformation:
	aws cloudformation $(COMMAND) \
	--stack-name Umphbase \
	--template-body file://template.yaml \
	--parameters \
	ParameterKey=BucketName,ParameterValue=$(UMPHBASE_BUCKET) \
	ParameterKey=DeploymentBucketName,ParameterValue=$(DEPLOYMENT_BUCKET) \
	ParameterKey=DBUsername,ParameterValue=$(DB_USERNAME) \
	ParameterKey=DBPassword,ParameterValue=$(DB_PASSWORD) \
	--capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM

# Create CloudFormation stack
create-stack:
	make cloudformation COMMAND=create-stack

# Update CloudFormation stack
update-stack:
	make cloudformation COMMAND=update-stack
# Set Make variables from .env file
include .env
export

# Get the full function name from the cloudformation stack
define host_name
	aws rds describe-db-instances --db-instance-identifier umphbase \
	| jq ."DBInstances" | jq ".[0]" | jq ."Endpoint" | jq ."Address" |
endef

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

# Upload a local ATU pull to the AWS RDS Database (Warning: Overwrites!)
upload:
	$(call host_name) \
	xargs -I {} cd .. && python upload.py \
	--method args --path atu_cleaned \
	--host {} --database umphbase \
	--user $(DB_USERNAME) --password $(DB_PASSWORD)

# Initialize the AWS RDS Database with a fresh local pull from ATU
init:
	cd .. && python pull.py
	cd .. && python clean.py
	make upload

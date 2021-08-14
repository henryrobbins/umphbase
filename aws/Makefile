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

# Adds the email address to the list of identities in SES
email:
	aws ses verify-email-identity --email-address $(EMAIL)

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
	ParameterKey=Email,ParameterValue=$(EMAIL) \
	--capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM

# Create CloudFormation stack
create-stack:
	make cloudformation COMMAND=create-stack

# Update CloudFormation stack
update-stack:
	make cloudformation COMMAND=update-stack

# Upload a local ATU pull to the AWS RDS Database (Warning: Overwrites!)
upload:
	cd .. && $(call host_name) \
	xargs -I {} python upload.py \
	--method args --path atu_cleaned \
	--host {} --database umphbase \
	--user $(DB_USERNAME) --password $(DB_PASSWORD)

# Initialize the AWS RDS Database with a fresh local pull from ATU
init:
	cd .. && python pull.py
	cd .. && python clean.py
	make upload

# Download and unzip the .sql file backup of the AWS RDS Database
download:
	curl https://$(UMPHBASE_BUCKET).s3.$(REGION).amazonaws.com/umphbase.sql.gz \
	--output umphbase.sql.gz
	gzip -d umphbase.sql.gz
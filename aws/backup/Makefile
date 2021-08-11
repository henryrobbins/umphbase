# Set Make variables from .env file
include ../.env
export

# Get the full function name from the cloudformation stack
define function_name
	aws cloudformation describe-stack-resources \
	--stack-name Umphbase --logical-resource-id Backup \
	| jq .'StackResources' | jq '.[0]' | jq .'PhysicalResourceId' |
endef

# Create a zip directory with lambda function source code.
zip:
	rm -rf backup.zip
	zip backup.zip main.py
	zip backup.zip backup.sh
	zip backup.zip mysqldump

# Upload the lambda function source code to the bucket.
upload:
	aws s3api put-object --bucket $(DEPLOYMENT_BUCKET) --key backup.zip \
	--body backup.zip

# Update the lambda function with the source code from the bucket.
update:
	$(call function_name) \
	xargs -I {} aws lambda update-function-code --function-name {} \
	--s3-bucket $(DEPLOYMENT_BUCKET)  --s3-key backup.zip

# Deploy the current source code.
deploy: zip upload update

# Invoke the lambda function.
invoke:
	$(call function_name) \
	xargs -I {} aws lambda invoke --function-name {} \
	--cli-connect-timeout 6000 --cli-read-timeout 6000 \
	output.json
# Set Make variables from .env file
include ../.env
export

# Get the full function name from the cloudformation stack
define function_name
	aws cloudformation describe-stack-resources \
	--stack-name Umphbase --logical-resource-id Update \
	| jq .'StackResources' | jq '.[0]' | jq .'PhysicalResourceId' |
endef

# Create a zip directory with lambda function source code.
zip:
	rm -rf update.zip
	zip update.zip main.py
	zip update.zip ../../atu.py
	zip update.zip ../../clean.py
	zip update.zip ../../sql_util.py
	zip update.zip ../../update.py


# Upload the lambda function source code to the bucket.
upload:
	aws s3api put-object --bucket $(DEPLOYMENT_BUCKET) --key update.zip \
	--body update.zip

# Update the lambda function with the source code from the bucket.
update:
	$(call function_name) \
	xargs -I {} aws lambda update-function-code --function-name {} \
	--s3-bucket $(DEPLOYMENT_BUCKET)  --s3-key update.zip

# Deploy the current source code.
deploy: zip upload update

# Invoke the lambda function.
invoke:
	$(call function_name) \
	xargs -I {} aws lambda invoke --function-name {} \
	--cli-connect-timeout 6000 --cli-read-timeout 6000 \
	output.json
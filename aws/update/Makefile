# Set Make variables from .env file
include ../.env
export

# Create a zip directory with lambda function source code
zip:
	rm -rf update.zip
	zip update.zip update.py
	zip update.zip ../../pull.py
	zip update.zip ../../sql_push.py

# Update the lambda function source code.
deploy:
	aws s3api put-object --bucket $(UPDATE_BUCKET) --key update.zip \
	--body update.zip

# Invoke the lambda function
invoke:
	aws cloudformation describe-stack-resources \
	--stack-name Umphbase --logical-resource-id Backup \
	| jq .'StackResources' | jq '.[0]' | jq .'PhysicalResourceId' | \
	xargs -I {} aws lambda invoke --function-name {} \
	--cli-connect-timeout 6000 --cli-read-timeout 6000 \
	output.json
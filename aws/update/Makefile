# Set Make variables from .env file
include ../.env
export

# Create a zip directory with lambda function source code
zip:
	rm -rf update.zip
	zip update.zip main.py
	zip update.zip ../../atu.py
	zip update.zip ../../clean.py
	zip update.zip ../../sql_util.py
	zip update.zip ../../update.py

# Update the lambda function source code.
deploy:
	aws s3api put-object --bucket $(DEPLOYMENT_BUCKET) --key update.zip \
	--body update.zip

# Invoke the lambda function
invoke:
	aws cloudformation describe-stack-resources \
	--stack-name Umphbase --logical-resource-id Update \
	| jq .'StackResources' | jq '.[0]' | jq .'PhysicalResourceId' | \
	xargs -I {} aws lambda invoke --function-name {} \
	--cli-connect-timeout 6000 --cli-read-timeout 6000 \
	output.json
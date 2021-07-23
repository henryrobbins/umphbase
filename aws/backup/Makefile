# Set Make variables from .env file
include ../.env
export

# Create a zip directory with lambda function source code.
zip:
	rm -rf backup.zip
	zip backup.zip backup.py
	zip backup.zip backup.sh
	zip backup.zip mysqldump

# Update the lambda function source code.
deploy:
	aws s3api put-object --bucket $(BACKUP_BUCKET) --key backup.zip \
	--body backup.zip

# Invoke the lambda function.
invoke:
	aws cloudformation describe-stack-resources \
	--stack-name Umphbase --logical-resource-id Backup \
	| jq .'StackResources' | jq '.[0]' | jq .'PhysicalResourceId' | \
	xargs -I {} aws lambda invoke --function-name {} \
	--cli-connect-timeout 6000 --cli-read-timeout 6000 \
	output.json
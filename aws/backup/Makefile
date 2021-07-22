# Note: Database names must be globally unique
BACKUP_BUCKET=umphbase-backup-source

# Create a zip directory with lambda function source code.
lambda:
	rm -rf backup.zip
	zip backup.zip backup.py
	zip backup.zip backup.sh
	zip backup.zip mysqldump

# Update the lambda function source code.
deploy:
	aws s3api put-object --bucket $(BACKUP_BUCKET) --key backup.zip \
	--body backup.zip

# TODO: this will not work because incorrect function name
# Invoke the lambda function.
invoke:
	aws lambda invoke --function-name Backup output.json
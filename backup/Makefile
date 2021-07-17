# Create a zip directory with lambda function source code.
lambda:
	rm -rf backup.zip
	zip backup.zip backup.py
	zip backup.zip backup.sh
	zip backup.zip mysqldump

# Update the lambda function source code.
deploy: zip
	aws lambda update-function-code --function-name BackupUmphbase \
	--zip-file fileb://backup.zip

# Invoke the lambda function.
invoke:
	aws lambda invoke --function-name BackupUmphbase output.json
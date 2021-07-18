import os

# AWS Account ID
# https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html
AWS_ID = "380560785783"

# Create directory for configuration file
directory = 'configs'
if not os.path.exists(directory):
    os.makedirs(directory)

# Substitute in AWS Account ID for all configuration files
for filename in os.listdir('.'):
    if filename not in ['substitute.py', 'Makefile', directory]:
        with open(filename, "r") as file:
            new_filename = '%s/%s' % (directory, filename)
            with open(new_filename, 'w') as new_file:
                new_file.write(file.read().replace('[AWS_ID]', AWS_ID))

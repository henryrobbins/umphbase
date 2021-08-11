# Lambda Layer

This [Lambda Layer](https://docs.aws.amazon.com/lambda/latest/dg/invocation-layers.html)
includes Python packages needed by the
[Update Lambda Function](../update/README.md). A comprehensive list of packages
is included below.

| Package       | Use                                                  |
| ------------- | ---------------------------------------------------- |
| numpy         | Data cleaning and transformation                     |
| pandas        | Maintaining and transforming data                    |
| pymysql       | Connecting to and querying MySQL databases           |
| requests      | Making HTTP requests to the ATU API                  |
| xmltodict     | Interpreting XML output from the ATU API             |

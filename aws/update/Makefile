# Note: Database names must be globally unique
UPDATE_BUCKET=umphbase-update-source
FUNC_NAME=Update
PKG_NAME=layer
PKG_DIR=$(PKG_NAME)/python/lib/python3.8/site-packages
NUMPY=numpy-1.21.0-cp38-cp38-manylinux_2_5_x86_64.manylinux1_x86_64.whl
PANDAS=pandas-1.3.0-cp38-cp38-manylinux_2_5_x86_64.manylinux1_x86_64.whl

# Must install numpy in this way to work with AWS lambda
# https://korniichuk.medium.com/lambda-with-pandas-fd81aa2ff25e
numpy:
	curl https://files.pythonhosted.org/packages/97/84/\
	3aeca9d6363e017557d1f1e753517b79700e235acae0be797d9f5a1273dc/$(NUMPY) \
	--output $(PKG_DIR)/$(NUMPY)
	cd $(PKG_DIR) && unzip $(NUMPY)

# Must install pandas in this way to work with AWS lambda
# https://korniichuk.medium.com/lambda-with-pandas-fd81aa2ff25e
pandas:
	curl https://files.pythonhosted.org/packages/76/3f/\
	eff98f997ed710250fb59b25f5cb2d1853335d953644f0ad262f9555a59a/$(PANDAS) \
	--output $(PKG_DIR)/$(PANDAS)
	cd $(PKG_DIR) && unzip $(PANDAS)

# Create a zip directory with lambda layer source code
layer:
	rm -rf $(PKG_NAME)
	mkdir -p $(PKG_DIR)
	make numpy
	make pandas
	pip install -t $(PKG_DIR) pytz
	pip install -t $(PKG_DIR) pymysql
	pip install -t $(PKG_DIR) requests
	pip install -t $(PKG_DIR) xmltodict
	cd $(PKG_DIR) && rm -r *.whl *.dist-info __pycache__
	cd $(PKG_NAME) && zip -r $(PKG_NAME).zip python

# Create a zip directory with lambda function source code
lambda:
	rm -rf update.zip
	zip update.zip update.py
	zip update.zip pull.py
	zip update.zip sql_push.py

# Create zip directories for both lambda function and layer
all: layer lambda

# Update the lambda function source code.
deploy-lambda:
	aws s3api put-object --bucket $(UPDATE_BUCKET) --key update.zip \
	--body update.zip

# Deploy lambda layer and update lambda function layers
deploy-layer:
	aws lambda publish-layer-version --layer-name $(PKG_NAME) \
	--zip-file fileb://$(PKG_NAME)/$(PKG_NAME).zip \
	--compatible-runtimes python3.8 | jq '.LayerVersionArn' | \
	xargs -I {}  aws lambda update-function-configuration \
	--function-name $(FUNC_NAME) --layers {}

# Deploy both the lambda function and layer
deploy: deploy-lambda deploy-layer

# Invoke the lambda function
invoke:
	aws lambda invoke --function-name \
	$(aws cloudformation describe-stack-resources \
	--stack-name Umphbase --logical-resource-id Update \
	| jq .'StackResources' | jq '.[0]' | jq .'PhysicalResourceId') \
	--cli-connect-timeout 6000 --cli-read-timeout 6000 \
	output.json
# Set Make variables from .env file
include ../.env
export

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
zip:
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

# Update the lambda layer source code
deploy:
	aws s3api put-object --bucket $(DEPLOYMENT_BUCKET) --key layer.zip \
	--body layer/layer.zip
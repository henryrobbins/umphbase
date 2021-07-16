PKG_DIR=packages
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

# TODO: Make work with layer
# pip install -t common-lib/python -r requirements.txt
# cd common-lib/python && rm -r *.dist-info __pycache__
# cd common-lib && zip -r ../common-lib.zip .

# Create a zip directory with lambda layer source code.
# https://medium.com/@avijitsarkar123/
# how-lambda-layer-reduced-my-deployment-package-size-b571ebff79f1
dependencies:
	rm -rf packages
	mkdir -p $(PKG_DIR)
	make numpy
	make pandas
	cd $(PKG_DIR) && pip install -t . pytz
	cd $(PKG_DIR) && pip install -t . pymysql
	cd $(PKG_DIR) && pip install -t . requests
	cd $(PKG_DIR) && pip install -t . xmltodict
	cd $(PKG_DIR) && rm -r *.whl *.dist-info __pycache__

# Create a zip directory with lambda function source code.
lambda:
	rm -rf update.zip
	zip update.zip update.py
	zip update.zip pull.py
	zip update.zip sql_push.py
	zip update.zip update.sh
	cd $(PKG_DIR) && zip -r ../update.zip .

# Update the lambda function source code.
update_lambda:
	aws lambda update-function-code --function-name UpdateUmphbase \
	--zip-file fileb://update.zip

# TODO: Make work with layer
# Update the layer source code.
update_layer:
	aws lambda publish-layer-version --layer-name common-lib \
	--zip-file fileb://common-lib.zip --compatible-runtimes python3.8

# Invoke the lambda function.
invoke:
	aws lambda invoke --function-name UpdateUmphbase output.json \
	--cli-connect-timeout 6000 --cli-read-timeout 6000
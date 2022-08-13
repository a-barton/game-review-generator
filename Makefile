export PROJECT_NAME := game-review-generator
export PROJECT_ALIAS := grg

export STACK_NAME = $(PROJECT_NAME)

export APPLICATION_HOME := ${PWD}
export CONTAINER_NAME := ${PROJECT_NAME}
export CONTAINER_VERSION := latest
export CONTAINER_TEST_DIR := ${PWD}/tests/test_container_mount
export MODEL_SOURCE_BUCKET := game-review-generator-fine-tuned-model

##############################
## Install / Initialisation ##
##############################

bucket-setup:
	@echo "Retrieving model and syncing to provided S3 bucket..."
	@python scripts/bucket_setup.py --parameters parameters.json --model_source_bucket ${MODEL_SOURCE_BUCKET}

init: bucket-setup
	conda env create -f environment.yaml -n $(PROJECT_ALIAS) \
		|| \
	conda env update -f environment.yaml -n $(PROJECT_ALIAS)

environment.yaml:
	conda env export --no-builds > environment.yaml
.PHONY: environment.yaml


###########
## Tests ##
###########

tests:
	export AWS_ACCESS_KEY_ID='testing' && \
 	export AWS_SECRET_ACCESS_KEY='testing' && \
 	export AWS_SECURITY_TOKEN='testing' && \
 	export AWS_SESSION_TOKEN='testing' && \
	python -m pytest tests/ -v
.PHONY: tests

run-container-local-train:
	docker run -e "MODE=train" -v "${CONTAINER_TEST_DIR}:/src/src-container/artifacts/" "${CONTAINER_NAME}:${CONTAINER_VERSION}"

run-container-local-predict:
	docker run -e "APP_ID=362890" -v "${CONTAINER_TEST_DIR}:/src/src-container/artifacts/" "${CONTAINER_NAME}:${CONTAINER_VERSION}"

####################
## Build & Deploy ##
####################

container:
	docker build --tag="${CONTAINER_NAME}:${CONTAINER_VERSION}" src/src-container/.

configuration:
	@echo "Compiling the configuration files..."
	@python scripts/compile_configuration.py --parameters parameters.json
.PHONY: configuration

build:
	@echo "Compiling the CloudFormation template..."
	@python src/cloudformation/compile.py > .build/cfn.json

	@echo "Building application artifacts..."
	@python scripts/build_source.py --config .build/configuration/paths.json

remote:
	@python scripts/sync_with_remote.py --config .build/configuration/paths.json

infrastructure:
	aws cloudformation create-stack \
		--stack-name $(STACK_NAME) \
		--template-body file://.build/cfn.json \
		--parameters file://.build/configuration/cloudformation.json \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM

all: configuration build remote infrastructure

destroy:
	aws cloudformation delete-stack \
		--stack-name $(STACK_NAME)
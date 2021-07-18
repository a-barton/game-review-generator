export PROJECT_NAME := game-review-generator
export PROJECT_ALIAS := grg

export STACK_NAME = $(PROJECT_NAME)

export APPLICATION_HOME := ${PWD}
export CONTAINER_NAME := ${PROJECT_NAME}
export CONTAINER_VERSION := latest
export CONTAINER_TEST_DIR := ${PWD}/tests/test_container_mount

export S3_BUCKET := game-review-generator

##############################
## Install / Initialisation ##
##############################

init:
	conda env create -f environment.yaml -n $(PROJECT_ALIAS) \
		|| \
	conda env update -f environment.yaml -n $(PROJECT_ALIAS)

environment.yaml:
	conda env export --no-builds > environment.yaml
.PHONY: environment.yaml

###############
## Utilities ##
###############

format:
	black .

lambda:
	python scripts/scaffold.py lambda


###########
## Tests ##
###########

tests:
	python -m pytest tests/ -v
.PHONY: tests

####################
## Build & Deploy ##
####################

container:
	docker build --tag="${CONTAINER_NAME}:${CONTAINER_VERSION}" .

run-container-local:
	docker run -v "${CONTAINER_TEST_DIR}:/game-review-generator" "${CONTAINER_NAME}:${CONTAINER_VERSION}"

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
		--capabilities CAPABILITY_IAM

all: configuration build remote infrastructure

destroy:
	aws cloudformation delete-stack \
		--stack-name $(STACK_NAME)
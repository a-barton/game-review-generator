export PROJECT_NAME := game-review-generator
export PROJECT_ALIAS := grg

export STACK_NAME = $(PROJECT_NAME)

export APPLICATION_HOME := $(pwd)

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

build:
	@echo "Compiling the CloudFormation template..."
	@python src/cloudformation/compile.py > .build/cfn.json

	@echo "Building application artifacts..."
	@python scripts/build_source.py

infrastructure:
	aws cloudformation create-stack \
		--stack-name $(STACK_NAME) \
		--template-body file://.build/cfn.json \
		--parameters files://.build/cfn.parameters.json

all: build infrastructure

destroy:
	aws cloudformation delete-stack \
		--stack-name $(STACK_NAME)

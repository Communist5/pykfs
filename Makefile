DISTRIBUTION_NAME := pykfs
IGNORE_DIRECTORY := ignore

PYTHON_FILES = $(shell find . -name \*.py -not -path "./ignore/*" -not -path "./test/*" -not -name setup.py)

SAMPLE_ENV := $(IGNORE_DIRECTORY)/$(DISTRIBUTION_NAME)SampleEnv
SAMPLE_ENV_PIP := $(SAMPLE_ENV)/bin/pip
SAMPLE_ENV_PYTHON := $(SAMPLE_ENV)/bin/python

TEST_ENV := $(IGNORE_DIRECTORY)/$(DISTRIBUTION_NAME)TestEnv
TEST_ENV_PIP := $(TEST_ENV)/bin/pip
TEST_ENV_NOSE := $(TEST_ENV)/bin/nosetests
TEST_ENV_SITE_PACKAGES := $(TEST_ENV)/lib/python2.7/site-packages

DIST_DIR := dist

GZIP_COMMAND := tar -pczf
DATA_DIR := pykfs/data
SCRIPTS_DATA_DIR := $(DATA_DIR)/scripts
NEWPYDIST_DATA_SOURCE := $(SCRIPTS_DATA_DIR)/newpydist
NEWPYDIST_DATA_PACKAGE := $(SCRIPTS_DATA_DIR)/newpydist.tar.gz
NEWPYDIST_DATA_FILES := $(shell find . -path "$(NEWPYDIST_DATA_SOURCE)/*")
NEWPYDIST_DATA_NAMES := $(shell find "$(NEWPYDIST_DATA_SOURCE)" -mindepth 1 -maxdepth 1 -exec basename {} \;)

DATA_PACKAGES := $(NEWPYDIST_DATA_PACKAGE)

dist: setup.py $(PYTHON_FILES) requirements.txt README MANIFEST.in MAKEFILE $(DATA_PACKAGES)
	rm -f -r dist
	/usr/local/bin/python setup.py sdist 

.PHONY: sampleEnv
sampleEnv: $(SAMPLE_ENV)
$(SAMPLE_ENV): dist $(IGNORE_DIRECTORY)
	rm -f -r $(SAMPLE_ENV)
	virtualenv $(SAMPLE_ENV) --no-site-packages
	$(SAMPLE_ENV_PIP) install -e .

.PHONY: testEnv
testEnv: $(TEST_ENV) 
${TEST_ENV}: requirements.txt MAKEFILE $(IGNORE_DIRECTORY)
	rm -f -r $(TEST_ENV)
	virtualenv $(TEST_ENV) --no-site-packages
	$(TEST_ENV_PIP) install -r requirements.txt
	$(TEST_ENV_PIP) install mock
	$(TEST_ENV_PIP) install unittest2
	$(TEST_ENV_PIP) install nose
	ln -s ../../../../../pykfs $(TEST_ENV_SITE_PACKAGES)/pykfs 

.PHONY: clean
clean:
	rm -f -r $(DISTRIBUTION_NAME).egg-info build dist MANIFEST $(SAMPLE_ENV) $(TEST_ENV) $(DATA_PACKAGES)

.PHONY: pyshell
pyshell: $(SAMPLE_ENV)
	$(SAMPLE_ENV_PYTHON)

.PHONY: test
test: $(TEST_ENV)
	$(TEST_ENV_NOSE)

.PHONY: debug
debug: $(TEST_ENV)
	$(TEST_ENV_NOSE) -s

$(IGNORE_DIRECTORY):
	mkdir $(IGNORE_DIRECTORY)

.PHONY: data-archives
data-archives: $(DATA_PACKAGES)

$(NEWPYDIST_DATA_PACKAGE): $(NEWPYDIST_DATA_FILES) Makefile
	$(GZIP_COMMAND) $(NEWPYDIST_DATA_PACKAGE) -C $(NEWPYDIST_DATA_SOURCE) $(NEWPYDIST_DATA_NAMES)

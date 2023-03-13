SHELL := /bin/bash
SRC_DIR = "./src"

format:
	isort ${SRC_DIR}
	autopep8 --in-place --recursive ${SRC_DIR}
	brunette ${SRC_DIR}
	autoflake --recursive --in-place --remove-all-unused-imports ${SRC_DIR}

lint:
	export PYTHONPATH=${SRC_DIR} && pylint --rcfile setup.cfg ${SRC_DIR}
	export PYTHONPATH=${SRC_DIR} && flake8 ${SRC_DIR}
	brunette --check ${SRC_DIR}
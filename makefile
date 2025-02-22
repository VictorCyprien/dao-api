.PHONY: all requirements tests

all: requirements

run:
	export FLASK_APP=run; export FLASK_ENV=development; flask run --no-debugger --no-reload --host=0.0.0.0 --port=8081;

smtp:
	python -m smtpd -c DebuggingServer -n localhost:1025

shell:
	export FLASK_APP=run; export FLASK_ENV=development; flask shell;

build_schemas:
	export FLASK_APP=run; flask openapi write specs/dao-api-spec.json;
	export FLASK_APP=run; flask openapi write specs/dao-api-spec.yaml;

build_sdk:
	make build_schemas
	openapi-generator generate -i specs/dao-api-spec.yaml -g typescript-angular -o ../dao-mini-app/src/core/modules/dao-api

clean:
	@echo
	@echo "---- Clean *.pyc ----"
	@find . -name \*.pyc -delete

clean_pip: clean
	@echo
	@echo "---- Clean packages ----"
	@pip freeze | grep -v "^-e" | cut -d "@" -f1 | xargs pip uninstall -y

install:
	@echo
	@echo "---- Install packages from requirements.txt ----"
	@pip install -r requirements.txt
	@pip freeze
	@echo "---- Install packages from requirements.dev.txt ----"
	@pip install -r requirements.dev.txt
	@pip freeze
	@echo
	@echo "---- Install packages from setup ----"
	@$(shell echo ${PYTHON_ROCKSDB_FLAGS}) pip install -e ./

tests:
	pytest --cov=api --cov-config=.coveragerc --cov-report=html:htmlcov --cov-report xml:cov.xml --cov-report=term \
		-vv -W ignore::DeprecationWarning --doctest-modules --ignore-glob=./main.py --log-level=DEBUG --junitxml=report.xml ./ ./tests


testsx:
	pytest -x -vv -W ignore::DeprecationWarning --doctest-modules --ignore-glob=./api/main.py --log-level=DEBUG ./api ./tests

clean:
	rm -R venv

tree:
	tree -P "*.py" -I "venv|tests|__pycache__|dao_api.egg-info" --noreport
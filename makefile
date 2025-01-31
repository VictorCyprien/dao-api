install:
	python3 -m venv venv
	. venv/bin/activate; pip install -r requirements.txt

run:
	export FLASK_APP=run; export FLASK_ENV=development; flask run --no-debugger --host=0.0.0.0 --port=8081;

clean:
	rm -R venv

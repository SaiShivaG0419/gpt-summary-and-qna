createEnv:
	pip install virtualenv & \
		virtualenv ~/.venv

activateEnv:
	source ~/.venv/bin/activate

newEnv:
	createEnv activateEnv

install:
	python -m pip install --upgrade pip setuptools & \
		python -m pip install -r requirements.txt --no-cache-dir

test:
	python pytest --nbval src/*.ipynb

lint:
	pylint --disable=R,C src

format:
	black src

run-app:
	streamlit run frontend/main.py

all:
	install lint
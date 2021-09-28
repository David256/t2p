init:
	pip install -r requirements.txt

test:
	pytest

lint:
	flake8 t2p

typing:
	mypy

doc:
	make -C docs/ html

dev:
	pip3 install --editable .

resetdoc:
	sphinx-apidoc -o docs/source/ -F t2p

serve:
	python3 -m http.server -d docs/build/html

.PHONY: init test doc dev resetdoc serve lint
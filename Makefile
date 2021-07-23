init:
	pip install -r requirements.txt

test:
	pytest

doc:
	make -C docs/source html

dev:
	pip3 install --editable .

resetdoc:
	sphinx-apidoc -o docs/source/ -F t2p

serve:
	python3 -m http.server -d docs/source/_build/html

.PHONY: init test doc dev resetdoc serve
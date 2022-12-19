# pip install --user twine
python setup.py sdist
twine upload dist/* -r pypitest

# pip install --user twine

# upload to test
python setup.py sdist
twine upload dist/* -r pypitest

# upload to pypi
python setup.py sdist bdist_wheel --universal
twine upload dist/* -r pypi

# add tag to git
git tag -a v1.0.0 -m "annotation for this release"
git push origin --tags

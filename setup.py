from distutils.core import setup

setup(
    name = 'hoi4_converter',
    packages = ['Hoi4Converter'],
    version = '1.1',  # Ideally should be same as your GitHub release tag varsion
    description = 'HOI4 Converter: A Python package for easier HOI4 Modding',
    author = 'Stefan Reiterer',
    author_email = 'stefan.harald.reiterer@gmail.com',
    url = 'https://github.com/maldun/hoi4_converter',
    download_url = 'https://github.com/maldun/hoi4_converter/archive/refs/tags/1.0.tar.gz',
    keywords = ['modding', 'Paradox'],
    license='GPL3',
    install_requires=[
          'pyparsing'
      ],
    classifiers = [],
) 

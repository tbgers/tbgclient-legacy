from setuptools import setup

setup(
    name='tbgclient',
    version='0.3-beta',
    description='A TBG API wrapper for Python.',
    author='Gilbert189',
    author_email='gilbertdannellelo@gmail.com',
    packages=['tbgclient', 'tbgclient.parsers'],  # same as name
    extras_require={
        'lxml': ['lxml'],
    },
)

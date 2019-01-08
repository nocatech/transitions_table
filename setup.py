from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='transitions_table',
    version='0.0.1',
    description='make a state transition table from a state machine made by transitions package.',
    long_description=readme,
    author='nocatech',
    install_requires=['pandas', 'transitions'],
    url='https://github.com/nocatech/transitions_table',
    license=license,
	packages=find_packages(exclude=['tests', 'test_*']),
	test_suite='tests'
)


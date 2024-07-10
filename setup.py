from setuptools import setup

setup(
    name='cron_utils',
    version='0.1',
    packages=['cron_utils'],
    include_package_data=True,  # Ensure package data is included
    install_requires=[
        'shared_config',
        'django',
        'paramiko',
        'djangorestframework',
        'pycryptodome',
        'django-environ',
        'pystache',
        'psycopg2',
        'requests',
        'paramiko',
        'openpyxl',
        'django-simple-history',
        'xmltodict',
        'openpyxl',
        'xlwt',
        'et-xmlfile'
        # Add any other dependencies as needed for the project
    ],
)

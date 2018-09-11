from setuptools import setup, find_packages

setup(
    name='dbchat',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click', 'pytz', 'cx_Oracle', 'plotly', 'delphixpy', 'ansible','boto3'
    ],
    entry_points='''
        [console_scripts]
        dbchat=dbchat.cli:cli
    ''',
)

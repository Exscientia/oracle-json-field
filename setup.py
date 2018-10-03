from distutils.core import Command
from setuptools import setup


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from django.conf import settings
        import os

        oracle_json_host = os.environ.get('ORACLE_JSON_HOST', 'localhost')
        oracle_json_port = os.environ.get('ORACLE_JSON_PORT', '1521')
        oracle_json_sid  = os.environ.get('ORACLE_JSON_SID', 'orcl')
        oracle_json_user = os.environ.get('ORACLE_JSON_USER', 'test_user')
        oracle_json_pass = os.environ.get('ORACLE_JSON_PASS', 'test_pass')

        settings.configure(
            DATABASES={"default": {
              "ENGINE": "django.db.backends.oracle",
              "OPTIONS": {
                "threaded": True
              },
              "HOST": oracle_json_host,
              "PORT": oracle_json_port,
              "NAME": oracle_json_sid,
              "USER": oracle_json_user,
              "PASSWORD": oracle_json_pass
            }},
            INSTALLED_APPS=('oracle_json_field', 'django.contrib.contenttypes')
        )
        from django.core.management import call_command
        import django

        django.setup()
        call_command('test', 'oracle_json_field')


setup(
    name='oracle-json-field',
    version=__import__('oracle_json_field').__version__,
    packages=['oracle_json_field'],
    license='MIT',
    include_package_data=True,
    author='Vackar Afzal',
    author_email='vafzal@exscientia.co.uk',
    description='A JSON field for Oracle backends.',
    long_description=open("README.md").read(),
    install_requires=['Django >= 2.0.0'],
    tests_require=['Django >= 2.0.0'],
    cmdclass={'test': TestCommand},
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
    ],
)

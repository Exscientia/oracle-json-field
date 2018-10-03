
# Oracle Json Field
django_json_field is a reusable Django field that allows you to store validated JSON your database and your model
It is heavily inspired by the Postgres Json Field and this generic json field:
https://raw.githubusercontent.com/dmkoch/django-jsonfield/

## PreRequisites
To use oracle-json-field you will need Django 2.0+ and Python3+

## Installation
Install via pip

    pip install oracle-json-field

Or install via source

    python setup.py install

## Setup
Update Django settings as follows

    INSTALLED_APPS += ('oracle_json_field',)


## Define your models

    from oracle_json_field.fields import JSONField
    from oracle_json_field.managers import JsonQueryManager

    class JsonModel(models.Model):
        json = JSONField()
        default_json = JSONField(default={"key1": 50})
        complex_default_json = JSONField(default=[{"key1": 50}])
        empty_default = JSONField(default={})

        objects = JsonQueryManager()



## Create and **Natively** query any field in your json
    JsonModel.objects.create(json={
      "person": {
        "age": 25,
        "first_name": "Joe",
        "last_name": "Blogs",
        "address": {
          "number": "52",
          "street": "Here Terrace",
          "post_code": "ABC 123",
          "city": "Anytown",
          
        }
      }
    })
    
    JsonModel.objects.filter_json(json__person__first_name='Joe')
    JsonModel.objects.filter_json(json__person__first_name__startswith='J')
    JsonModel.objects.filter_json(json__person__address__city__in=['Anytown', 'Sometown'])
    JsonModel.objects.filter_json(json__person__age__gte=25)



## Running the test suite:
In order to run the test suite, you will need to create an oracle user
and export the following environment variables:

    ORACLE_JSON_HOST
    ORACLE_JSON_PORT
    ORACLE_JSON_SID
    ORACLE_JSON_USER
    ORACLE_JSON_PASS


This link describes how to setup the testing user:
https://code.djangoproject.com/wiki/OracleTestSetup

Then run the following command

    python setup.py test

You should then see:

    running test
    Creating test database for alias 'default'...
    Creating test user...
    System check identified no issues (0 silenced).
    ......................................
    Preserving test database for alias 'default'...
    ----------------------------------------------------------------------
    Ran 38 tests in 4.900s

    OK
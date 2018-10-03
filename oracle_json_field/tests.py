from django.db import models
from django.test import TestCase
from django.utils import timezone

# Create your tests here.
from .constants import JSON_TRUE, JSON_False
from .managers import JsonQueryManager
from .fields import JSONField


class JsonModel(models.Model):
    json = JSONField()
    default_json = JSONField(default={"key1": 50})
    complex_default_json = JSONField(default=[{"key1": 50}])
    empty_default = JSONField(default={})

    objects = JsonQueryManager()


class BaseJSONFieldTest(TestCase):

    def setUp(self):
        JsonModel.objects.all().delete()

    def _create_and_fetch(self, json_obj):
        JsonModel.objects.create(json=json_obj)
        db_obj = JsonModel.objects.latest('id')
        return db_obj


class JSONFieldCreateTest(BaseJSONFieldTest):
    """JSONField Wrapper Tests"""

    def test_simple_create(self):
        """Test saving a JSON object in teh JSONField"""
        json_obj = {
            'item_1': 'this is a json blah',
            'something_else': 'Hello'
        }

        obj = JsonModel.objects.create(json=json_obj)
        new_obj = JsonModel.objects.get(id=obj.id)

        self.assertEqual(new_obj.json, json_obj)
        self.assertEqual(new_obj.default_json, {"key1": 50})
        self.assertEqual(new_obj.complex_default_json, [{"key1": 50}])
        self.assertEqual(new_obj.empty_default, {})

    def test_create_str(self):
        db_obj = self._create_and_fetch({'item_1': 'A string'})
        self.assertEquals(db_obj.json['item_1'], 'A string')

    def test_create_int(self):
        db_obj = self._create_and_fetch({'item_1': 22})
        self.assertEquals(db_obj.json['item_1'], 22)

    def test_create_float(self):
        db_obj = self._create_and_fetch({'item_1': 11.59})
        self.assertEquals(db_obj.json['item_1'], 11.59)

    def test_create_zero(self):
        db_obj = self._create_and_fetch({'item_1': 0})
        self.assertEquals(db_obj.json['item_1'], 0)

    def test_create_null(self):
        db_obj = self._create_and_fetch({'item_1': None})
        self.assertEquals(db_obj.json['item_1'], None)

    def test_create_date(self):
        now = timezone.now()
        db_obj = self._create_and_fetch({'item_1': now})
        self.assertEquals(db_obj.json['item_1'], now.isoformat())


class BaseJSONFieldQueryTestCase(BaseJSONFieldTest):

    def setUp(self):
        super().setUp()
        self.test_data = [
            {'_id': 1,  'x_str': 'A string 1',   'x_int': 5,     'x_float': 1.5, 'x_null': None, 'x_bool': True},
            {'_id': 2,  'x_str': 'A string 2',   'x_int': 33,    'x_float': 2.5, 'x_null': None, 'x_bool': True},
            {'_id': 3,  'x_str': 'A string 3',   'x_int': 54,    'x_float': 3.5, 'x_null': None, 'x_bool': True},
            {'_id': 4,  'x_str': 'A string 4',   'x_int': 59,    'x_float': 4.5, 'x_null': None, 'x_bool': True},
            {'_id': 5,  'x_str': 'A string 5',   'x_int': 65,    'x_float': 5.5, 'x_null': None, 'x_bool': True},
            {'_id': 6,  'x_str': 'A string 6',   'x_int': 220,   'x_float': 6.5, 'x_null': None, 'x_bool': True},
            {'_id': 7,  'x_str': 'A string 7',   'x_int': 330,   'x_float': 7.5, 'x_null': None, 'x_bool': True},
            {'_id': 8,  'x_str': 'A string 8',   'x_int': 550,   'x_float': 8.5, 'x_null': None, 'x_bool': True},
            {'_id': 9,  'x_str': 'A string 9',   'x_int': 5214,  'x_float': 9.5, 'x_null': {},   'x_bool': False},
            {'_id': 10, 'x_str': 'A string 10',  'x_int': 96544, 'x_float': 10.5,'x_null': {},   'x_bool': False},

        ]
        for item in self.test_data:
            self._create_and_fetch(item)


class StrJSONFieldQueryTestCase(BaseJSONFieldQueryTestCase):

    def test_exact(self):
        lookup = JsonModel.objects.filter_json(json__x_str='A string 1')
        self.assertEquals(lookup.count(), 1)

    def test_iexact(self):
        lookup = JsonModel.objects.filter_json(json__x_str__iexact='a string 1')
        self.assertEquals(lookup.count(), 1)

    def test_contains(self):
        lookup = JsonModel.objects.filter_json(json__x_str__contains='ng 1')
        self.assertEquals(lookup.count(), 2)

    def test_startswith(self):
        lookup = JsonModel.objects.filter_json(json__x_str__startswith='A string')
        self.assertEquals(lookup.count(), 10)

    def test_endswith(self):
        lookup = JsonModel.objects.filter_json(json__x_str__endswith='8')
        self.assertEquals(lookup.count(), 1)

    def test_in(self):
        lookup = JsonModel.objects.filter_json(json__x_str__in=['A string 1'])
        self.assertEquals(lookup.count(), 1)

    def test_in_no_matches(self):
        lookup = JsonModel.objects.filter_json(json__x_str__in=['A string 1 dsds'])
        self.assertEquals(lookup.count(), 0)

    def test_in_extra_vals(self):
        lookup = JsonModel.objects.filter_json(json__x_str__in=['A string 1', 'A string 1 dsds'])
        self.assertEquals(lookup.count(), 1)

    def test_in_multi_matches(self):
        lookup = JsonModel.objects.filter_json(json__x_str__in=['A string 1', 'A string 2'])
        self.assertEquals(lookup.count(), 2)


class IntJSONFieldQueryTestCase(BaseJSONFieldQueryTestCase):

    def test_exact(self):
        lookup = JsonModel.objects.filter_json(json__x_int=59)
        self.assertEquals(lookup.count(), 1)
        self.assertEquals(lookup[0].json['x_int'], 59)

    def test_gt(self):
        lookup = JsonModel.objects.filter_json(json__x_int__gt=65)
        self.assertEquals(lookup.count(), 5)

    def test_gte(self):
        lookup = JsonModel.objects.filter_json(json__x_int__gte=65)
        self.assertEquals(lookup.count(), 6)

    def test_lt(self):
        lookup = JsonModel.objects.filter_json(json__x_int__lt=59)
        self.assertEquals(lookup.count(), 3)

    def test_lte(self):
        lookup = JsonModel.objects.filter_json(json__x_int__lte=59)
        self.assertEquals(lookup.count(), 4)


class FloatJSONFieldQueryTestCase(BaseJSONFieldQueryTestCase):

    def test_exact(self):
        lookup = JsonModel.objects.filter_json(json__x_float=9.5)
        self.assertEquals(lookup.count(), 1)

    def test_gt(self):
        lookup = JsonModel.objects.filter_json(json__x_float__gt=9.5)
        self.assertEquals(lookup.count(), 1)

    def test_gte(self):
        lookup = JsonModel.objects.filter_json(json__x_float__gte=9.5)
        self.assertEquals(lookup.count(), 2)

    def test_lt(self):
        lookup = JsonModel.objects.filter_json(json__x_float__lt=4.5)
        self.assertEquals(lookup.count(), 3)

    def test_lte(self):
        lookup = JsonModel.objects.filter_json(json__x_float__lte=4.5)
        self.assertEquals(lookup.count(), 4)


class NullJSONFieldQueryTestCase(BaseJSONFieldQueryTestCase):

    def test_is_null(self):
        lookup = JsonModel.objects.filter_json(json__x_null__isnull=True)
        self.assertEquals(lookup.count(), 8)

    def test_is_not_null(self):
        lookup = JsonModel.objects.filter_json(json__x_null__isnull=False)
        self.assertEquals(lookup.count(), 2)


class MultipleCallsToFilter(BaseJSONFieldQueryTestCase):

    def test_simple(self):
        lookup = JsonModel.objects.filter(json__isnull=False)
        self.assertEquals(lookup.count(), 10)

    def test_json_then_simple(self):
        lookup = JsonModel.objects.filter(json__isnull=False).filter_json(json__x_null__isnull=False)
        self.assertEquals(lookup.count(), 2)

    def test_simple_then_json(self):
        lookup = JsonModel.objects.filter_json(json__x_null__isnull=False).filter(json__isnull=False)
        self.assertEquals(lookup.count(), 2)

    def test_json_then_json(self):
        lookup = JsonModel.objects.filter_json(json__x_null__isnull=False).filter_json(json__x_str='A string 10')
        self.assertEquals(lookup.count(), 1)


class BooleanJSONFieldQueryTestCase(BaseJSONFieldQueryTestCase):

    def test_is_true(self):
        lookup = JsonModel.objects.filter_json(json__x_bool=JSON_TRUE)
        self.assertEquals(lookup.count(), 8)

    def test_is_false(self):
        lookup = JsonModel.objects.filter_json(json__x_bool=JSON_False)
        self.assertEquals(lookup.count(), 2)


class NestedJSONFieldQueryTestCase(BaseJSONFieldQueryTestCase):

    def setUp(self):
        super().setUp()
        self.example1 = {'l1': {'x_str': 'A Value 1', 'x_float': 22.5, 'l2': {'x_str': 'A Value L2 A', 'x_float': 4.5}}}
        self.example2 = {'l1': {'x_str': 'A Value 2', 'x_float': 17.5, 'l2': {'x_str': 'A Value L2 B', 'x_float': 2.1}}}
        self._create_and_fetch(self.example1)
        self._create_and_fetch(self.example2)

    def test_nested_str(self):
        lookup = JsonModel.objects.filter_json(json__l1__x_str='A Value 1')
        self.assertEquals(lookup.count(), 1)

    def test_nested_float(self):
        lookup = JsonModel.objects.filter_json(json__l1__x_float=22.5)
        self.assertEquals(lookup.count(), 1)

    def test_nested_float_gt(self):
        lookup = JsonModel.objects.filter_json(json__l1__x_float__gt=22.5)
        self.assertEquals(lookup.count(), 0)

    def test_nested_float_gte(self):
        lookup = JsonModel.objects.filter_json(json__l1__x_float__gte=22.5)
        self.assertEquals(lookup.count(), 1)

    def test_deeply_nested_str(self):
        lookup = JsonModel.objects.filter_json(json__l1__l2__x_str='A Value L2 A')
        self.assertEquals(lookup.count(), 1)

    def test_deeply_nested_float(self):
        lookup = JsonModel.objects.filter_json(json__l1__l2__x_float=4.5)
        self.assertEquals(lookup.count(), 1)

    def test_deeply_nested_float_gt(self):
        lookup = JsonModel.objects.filter_json(json__l1__l2__x_float__gt=3)
        self.assertEquals(lookup.count(), 1)

    def test_multiple_predicates(self):
        lookup = JsonModel.objects.filter_json(json__l1__x_str='A Value 1', json__l1__l2__x_str='A Value L2 A')
        self.assertEquals(lookup.count(), 1)
        self.assertDictEqual(lookup.first().json, self.example1)




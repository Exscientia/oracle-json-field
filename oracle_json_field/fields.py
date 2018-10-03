import json


from .encoders import JSONEncoder
from django.core import exceptions
from django.db.models import TextField, FloatField, Transform, lookups as builtin_lookups
from django.utils.translation import gettext_lazy as _
from django.db.backends.oracle.base import DatabaseWrapper
from django.db.models import lookups

__all__ = ['JSONField']

DatabaseWrapper.data_type_check_constraints['JSONField'] = '%(qn_column)s IS JSON'


class JSONField(TextField):
    empty_strings_allowed = False
    description = _('A JSON object')
    default_error_messages = {
        'invalid': _("Value must be valid JSON."),
    }
    _default_hint = ('dict', '{}')

    def __init__(self, verbose_name=None, name=None, encoder=None, **kwargs):
        if encoder and not callable(encoder):
            raise ValueError("The encoder parameter must be a callable object.")
        self.encoder = encoder or JSONEncoder
        super().__init__(verbose_name, name, **kwargs)

    def db_type(self, connection):
        return 'clob'

    def get_internal_type(self):
        return 'JSONField'

    def db_parameters(self, connection):
        """
        Extension of db_type(), providing a range of different return values
        (type, checks). This will look at db_type(), allowing custom model
        fields to override it.
        """
        defaults = super().db_parameters(connection)
        return defaults

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.encoder is not None:
            kwargs['encoder'] = self.encoder
        return name, path, args, kwargs

    def get_transform(self, name):
        transform = super().get_transform(name)
        if transform:
            return transform
        return KeyTransformFactory(name)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return json.loads(str(value))

    def to_python(self, value):
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            return json.loads(value)

        if value is None:
            return value

    def get_prep_value(self, value):
        if value is not None:
            return json.dumps(value, cls=self.encoder)
        return value

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        options = {'cls': self.encoder} if self.encoder else {}
        try:
            json.dumps(value, **options)
        except TypeError:
            raise exceptions.ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={'value': value},
            )

    def value_to_string(self, obj):
        return self.value_from_object(obj)

    def formfield(self, **kwargs):
        return super().formfield(**{**kwargs})


class KeyTransform(Transform):
    operator = '.'
    nested_operator = '.'

    def __init__(self, key_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_name = key_name

    def as_sql(self, compiler, connection):
        key_transforms = [self.key_name]
        previous = self.lhs
        while isinstance(previous, KeyTransform):
            key_transforms.insert(0, previous.key_name)
            previous = previous.lhs
        lhs, params = compiler.compile(previous)
        if len(key_transforms) > 1:
            quoted_keys = map(lambda x: '"{0}"'.format(x), key_transforms)
            sql = "(%s%s%s)" % (lhs, self.nested_operator, self.nested_operator.join(quoted_keys))
            return sql, params
        try:
            int(self.key_name)
        except ValueError:
            lookup = "%s" % self.key_name
        else:
            lookup = "%s" % self.key_name
        return "(%s%s%s)" % (lhs, self.operator, lookup), params


class KeyTextTransform(KeyTransform):
    operator = '.'
    nested_operator = '.'
    output_field = TextField()




class KeyFloatTransform(KeyTransform):
    operator = '.'
    nested_operator = '.'
    output_field = FloatField()


class KeyTransformTextLookupMixin:
    def __init__(self, key_transform, *args, **kwargs):
        assert isinstance(key_transform, KeyTransform)
        key_text_transform = KeyTextTransform(
            key_transform.key_name, *key_transform.source_expressions, **key_transform.extra
        )
        super().__init__(key_text_transform, *args, **kwargs)


class KeyTransformFloatLookupMixin:
    def __init__(self, key_transform, *args, **kwargs):
        assert isinstance(key_transform, KeyTransform)
        key_text_transform = KeyFloatTransform(
            key_transform.key_name, *key_transform.source_expressions, **key_transform.extra
        )
        super().__init__(key_text_transform, *args, **kwargs)


class KeyTransformIn(KeyTransformTextLookupMixin, builtin_lookups.In):
    pass


class KeyTransformIExact(KeyTransformTextLookupMixin, builtin_lookups.IExact):
    pass


class KeyTransformExact(KeyTransformTextLookupMixin, builtin_lookups.Exact):
    pass


class KeyTransformIContains(KeyTransformTextLookupMixin, builtin_lookups.IContains):
    pass


class KeyTransformStartsWith(KeyTransformTextLookupMixin, builtin_lookups.StartsWith):
    pass


class KeyTransformIStartsWith(KeyTransformTextLookupMixin, builtin_lookups.IStartsWith):
    pass


class KeyTransformEndsWith(KeyTransformTextLookupMixin, builtin_lookups.EndsWith):
    pass


class KeyTransformIEndsWith(KeyTransformTextLookupMixin, builtin_lookups.IEndsWith):
    pass


class KeyTransformRegex(KeyTransformTextLookupMixin, builtin_lookups.Regex):
    pass


class KeyTransformIRegex(KeyTransformTextLookupMixin, builtin_lookups.IRegex):
    pass


class KeyTransformGreaterThan(KeyTransformFloatLookupMixin, builtin_lookups.GreaterThan):
    pass


class KeyTransformGreaterThanOrEqual(KeyTransformFloatLookupMixin, builtin_lookups.GreaterThanOrEqual):
    pass


class KeyTransformLessThan(KeyTransformFloatLookupMixin, builtin_lookups.LessThan):
    pass


class KeyTransformLessThanOrEqual(KeyTransformFloatLookupMixin, builtin_lookups.LessThanOrEqual):
    pass


class KeyTransformFactory:

    def __init__(self, key_name):
        self.key_name = key_name

    def __call__(self, *args, **kwargs):
        return KeyTransform(self.key_name, *args, **kwargs)


def initialise_field():

    JSONField.register_lookup(lookups.GreaterThan)
    JSONField.register_lookup(lookups.GreaterThanOrEqual)
    JSONField.register_lookup(lookups.LessThan)
    JSONField.register_lookup(lookups.LessThanOrEqual)
    JSONField.register_lookup(lookups.Contains)
    JSONField.register_lookup(lookups.In)

    KeyTransform.register_lookup(KeyTransformIn)
    KeyTransform.register_lookup(KeyTransformExact)
    KeyTransform.register_lookup(KeyTransformIExact)
    KeyTransform.register_lookup(KeyTransformIContains)
    KeyTransform.register_lookup(KeyTransformStartsWith)
    KeyTransform.register_lookup(KeyTransformIStartsWith)
    KeyTransform.register_lookup(KeyTransformEndsWith)
    KeyTransform.register_lookup(KeyTransformIEndsWith)
    KeyTransform.register_lookup(KeyTransformRegex)
    KeyTransform.register_lookup(KeyTransformIRegex)
    KeyTransform.register_lookup(KeyTransformGreaterThan)
    KeyTransform.register_lookup(KeyTransformGreaterThanOrEqual)
    KeyTransform.register_lookup(KeyTransformLessThan)
    KeyTransform.register_lookup(KeyTransformLessThanOrEqual)


initialise_field()


from django.db import models


class JsonQuerySet(models.QuerySet):

    def filter_json(self, *args, **kwargs):
        """
        Similar to MyModel.objects.filter(...), but can also query json fields

        Examples:
            Given the following json blob:
                {
                    "address": {
                        "house_number": 60,
                        "line_1": "Some Terrace"
                        "line_2": "Some Town"
                        "Country": "Some Country"
                    }
                }
            Running this:
                MyModel.objects.filter_json(json_blob__address__house_number__gte=60)
                Would yield all objects with a house number greater than or equal to 60
        :param args:
        :param kwargs:
        :return: A queryset
        """
        # Note: Force a self join so that that table aliases are added, a requirement for json queries.
        # Can be removed if there is a cleaner mechanism to alias tables
        base_q = super().filter(*args, **kwargs)
        return self.filter(id__in=base_q.values_list('id', flat=True))


class JsonQueryManager(models.Manager):

    def get_queryset(self):
        return JsonQuerySet(self.model, using=self._db)

    def filter_json(self, *args, **kwargs):
        return self.get_queryset().filter_json(*args, **kwargs)

import django_filters

from companies.models import Company


class CompanyFilter(django_filters.FilterSet):
    class Meta:
        model = Company
        fields = {'name': ['exact', 'icontains'], 'owner': ['exact']}
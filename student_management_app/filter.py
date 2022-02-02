import django_filters

from .models import Staffs, Students
class StudentFilter(django_filters.FilterSet):
    class Meta:
        model = Students
        fields = '__all__'

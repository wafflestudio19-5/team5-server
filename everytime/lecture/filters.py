import django_filters
from django.forms.fields import MultipleChoiceField, CharField
from django.db.models import Q, F, Count

from everytime.exceptions import FieldError
from .models import Lecture, Department, LectureTime

GRADE_CHOICES =((0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6))

CLASSIFICATION_CHOICES = (
    ('전선', '전선'),
    ('교양', '교양'),
    ('일선', '일선'),
    ('전필', '전필'),
    ('논문', '논문'),
    ('대학원', '대학원'),
    ('교직', '교직'),
    ('공통', '공통'),
)


class LectureFilter(django_filters.FilterSet):
    grade = django_filters.MultipleChoiceFilter(choices=GRADE_CHOICES)
    classification = django_filters.MultipleChoiceFilter(choices=CLASSIFICATION_CHOICES)
    credits = NumInFilter()
    department = django_filters.ModelChoiceFilter(field_name='course__department',to_field_name='name', queryset=Department.objects.all())
    title = django_filters.CharFilter(field_name='course__title', lookup_expr='icontains', min_length=2)
    instructor = django_filters.CharFilter(field_name='course__instructor', lookup_expr='icontains', min_length=2)
    course_code = django_filters.CharFilter(field_name='course_code', lookup_expr='icontains')
    location = django_filters.CharFilter(field_name='lecturetime__location', lookup_expr='icontains')
    lecturetime = MultipleValueFilter(field_class=CharField, method='custom_time_filter')
    ordering = UserOrderingFilter(
        fields=(
            ('cart', 'cart'),
            ('course_code', 'course_code'),
        ),
    )

    class Meta:
        model = Lecture
        fields = {
            'classification':['exact'],
            'grade':['exact'],
            'credits':['in']
        }

    def custom_time_filter(self, queryset, value, *arg):
        q = Q()
        time_queryset = LectureTime.objects.filter(lecture__course__self_made=False)\
                        .select_related('lecture__course')
        for time_string in arg[0]:
            if len(time:=time_string.split('/')) != 3:
                raise FieldError('시간값이 요일/시작/끝 의 형식과 맞지 않습니다.')
            day = time[0]
            start = int(time[1])
            end = int(time[2])

            q.add(
                Q(day=day)&
                Q(start__gte=start)&
                Q(end__lte=end),
            q.OR)
        lecture_set = time_queryset.filter(~q).all().values('lecture')
        queryset = queryset.exclude(id__in=lecture_set)\
                .exclude(lecturetime=None)

        return queryset

class MultipleValueField(MultipleChoiceField):
    def __init__(self, *args, field_class, **kwargs):
        self.inner_field = field_class()
        super().__init__(*args, **kwargs)

    def valid_value(self, value):
        return self.inner_field.validate(value)

    def clean(self, values):
        return values and [self.inner_field.clean(value) for value in values]


class MultipleValueFilter(django_filters.filters.Filter):
    field_class = MultipleValueField

    def __init__(self, *args, field_class, **kwargs):
        kwargs.setdefault('lookup_expr', 'in')
        super().__init__(*args, field_class=field_class, **kwargs)


class NumInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class UserOrderingFilter(django_filters.OrderingFilter):
    """ Use Django 1.11 nulls_last feature to force nulls to bottom in all orderings. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 모델에 없는 필드를 허용하기 위해 여기에서 정보를 전달합니다.
        self.extra['choices'] += [
            ('competition', '-competition'),
            ('-competition', 'competition'),
            ('title','title'),
        ]


    def filter(self, queryset, value):
        if value and value[0] in ['competition', '-competition']:
            queryset = queryset.annotate(competition=F('cart')/F('quota'))
        if value and value[0] == 'title':
            value[0] = 'course__title'
        if value:
            f_ordering = []
            for o in value:
                if not o:
                    continue
                if o[0] == '-':
                    f_ordering.append(F(o[1:]).desc(nulls_last=True))
                else:
                    f_ordering.append(F(o).asc(nulls_last=True))

            return queryset.order_by(*f_ordering)

        return queryset


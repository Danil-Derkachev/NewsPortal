from django_filters import FilterSet, ModelChoiceFilter, DateFilter, CharFilter
from .models import Post, Category


class PostFilter(FilterSet):
    category = ModelChoiceFilter(
        field_name='postcategory__category',
        queryset=Category.objects.all(),
        label='Категории',
        empty_label='Все',
    )
    title = CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Заголовок содержит',
    )
    datetime = DateFilter(
        field_name='datetime',
        lookup_expr='gt',
        label='Дата больше чем (ГГГГ-ММ-ДД)',
    )

    class Meta:
        # В Meta классе мы должны указать Django модель,
        # в которой будем фильтровать записи.
        model = Post
        # В fields мы описываем по каким полям модели
        # будет производиться фильтрация.
        fields = {}

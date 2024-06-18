from django_filters import FilterSet, DateFilter, CharFilter, MultipleChoiceFilter, \
    ModelMultipleChoiceFilter

from .models import Post, Category, Author
from .resources import TYPES


class PostFilter(FilterSet):
    type = MultipleChoiceFilter(
        field_name='type',
        choices=TYPES,
        label='Тип публикации (Ctrl+ЛКМ)',
    )
    category = ModelMultipleChoiceFilter(
        field_name='postcategory__category',
        queryset=Category.objects.all(),
        label='Категории (Ctrl+ЛКМ)',
    )
    author_choice = ModelMultipleChoiceFilter(
        field_name='author',
        queryset=Author.objects.all(),
        label='Авторы (Ctrl+ЛКМ)',
    )
    author_search = CharFilter(
        field_name='author__user__username',
        lookup_expr='icontains',
        label='Имя автора содержит',
    )
    author_rating = CharFilter(
        field_name='author__rating',
        lookup_expr='gt',
        label='Рейтинг автора больше'
    )
    post_rating = CharFilter(
        field_name='rating',
        lookup_expr='gt',
        label='Рейтинг публикации больше',
    )
    title = CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Заголовок содержит',
    )
    text = CharFilter(
        field_name='text',
        lookup_expr='icontains',
        label='Текст содержит',
    )
    datetime = DateFilter(
        field_name='datetime',
        lookup_expr='gt',
        label='Опубликована позднее (ГГГГ-ММ-ДД)',
    )

    class Meta:
        # В Meta классе мы должны указать Django модель,
        # в которой будем фильтровать записи.
        model = Post
        # В fields мы описываем по каким полям модели
        # будет производиться фильтрация.
        fields = {}

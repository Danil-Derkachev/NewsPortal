from django.urls import path
from django.views.decorators.cache import cache_page

from . import views
from .views import *

urlpatterns = [
    path('', NewsList.as_view(), name='news_list'),
    path('news/create/', NewsCreate.as_view(), name='create_news'),
    path('news/<int:pk>', OneNewsDetail.as_view(), name='one_news'),
    path('news/<int:pk>/edit/', NewsEdit.as_view(), name='edit_news'),
    path('news/<int:pk>/delete/', NewsDelete.as_view(), name='delete_news'),
    path('news/subscribe_to_category', views.subscribe_to_category, name='subscribe_to_category'),
    path('news/unsubscribe_from_category', views.unsubscribe_from_category, name='unsubscribe_from_category'),

    path('article/create/', ArticleCreate.as_view(), name='create_article'),
    path('article/<int:pk>/edit/', ArticleEdit.as_view(), name='edit_article'),
    path('article/<int:pk>/delete/', ArticleEdit.as_view(), name='edit_article'),
]

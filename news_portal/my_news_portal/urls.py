from django.urls import path
# Импортируем созданное нами представление
from .views import *

urlpatterns = [
    path('', NewsList.as_view(), name='news_list'),
    path('news/search/', NewsList.as_view(), name='news_list'),
    path('news/create/', NewsCreate.as_view(), name='create_news'),
    path('news/<int:pk>', OneNewsDetail.as_view(), name='one_news'),
    path('news/<int:pk>/edit/', NewsEdit.as_view(), name='edit_news'),
    path('news/<int:pk>/delete/', NewsDelete.as_view(), name='delete_news'),

    path('articles/create/', ArticleCreate.as_view(), name='create_article'),
    path('articles/<int:pk>/edit/', ArticleEdit.as_view(), name='edit_article'),
    path('articles/<int:pk>/delete/', ArticleEdit.as_view(), name='edit_article'),
]

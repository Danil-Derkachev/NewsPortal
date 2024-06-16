from django.urls import path
from django.views.decorators.cache import cache_page

from . import views
from .views import *

urlpatterns = [
    path('', NewsList.as_view(), name='news_list'),
    path('news/create/', NewsCreate.as_view(), name='create_news'),
    path('news/<int:pk>', NewsDetail.as_view(), name='one_news'),
    path('news/<int:pk>/edit/', NewsEdit.as_view(), name='edit_news'),
    path('news/<int:pk>/delete/', NewsDelete.as_view(), name='delete_news'),
    path('news/<int:pk>/like/', views.like_post, name='like_post'),
    path('news/<int:pk>/dislike/', views.dislike_post, name='dislike_post'),

    path('category/subscribe', views.subscribe_to_category, name='subscribe_to_category'),
    path('category/unsubscribe', views.unsubscribe_from_category, name='unsubscribe_from_category'),

    path('comment/create', CommentCreate.as_view(), name='create_comment'),
    path('comment/<int:pk>/edit', CommentEdit.as_view(), name='edit_comment'),
    path('comment/<int:pk>', CommentDetail.as_view(), name='comment_detail'),
    path('comment/like', views.like_comment, name='like_comment'),
    path('comment/dislike', views.dislike_comment, name='dislike_comment'),
    path('comment/<int:pk>/delete', CommentDelete.as_view(), name='delete_comment'),

    path('article/create/', ArticleCreate.as_view(), name='create_article'),
    path('article/<int:pk>/edit/', ArticleEdit.as_view(), name='edit_article'),
    path('article/<int:pk>/delete/', ArticleEdit.as_view(), name='edit_article'),
]

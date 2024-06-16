from django.urls import path

from .views import *


urlpatterns = [
    path('', PostsList.as_view(), name='list_posts'),
    path('post/create/news', NewsCreate.as_view(), name='create_news'),
    path('post/create/article', ArticleCreate.as_view(), name='create_article'),
    path('post/<int:pk>', PostDetail.as_view(), name='detail_post'),
    path('post/<int:pk>/edit', PostEdit.as_view(), name='edit_post'),
    path('post/<int:pk>/delete', PostDelete.as_view(), name='delete_post'),
    path('post/<int:pk>/like', like_post, name='like_post'),
    path('post/<int:pk>/dislike', dislike_post, name='dislike_post'),

    path('category/<int:pk>/subscribe', subscribe_to_category, name='subscribe_to_category'),
    path('category/<int:pk>/unsubscribe', unsubscribe_from_category, name='unsubscribe_from_category'),

    path('comment/create', CommentCreate.as_view(), name='create_comment'),
    path('comment/<int:pk>/edit', CommentEdit.as_view(), name='edit_comment'),
    path('comment/<int:pk>/delete', CommentDelete.as_view(), name='delete_comment'),
    path('comment/<int:pk>/like', like_comment, name='like_comment'),
    path('comment/<int:pk>/dislike', dislike_comment, name='dislike_comment'),
]

from django.urls import path
# Импортируем созданное нами представление
from .views import NewsList, OneNewsDetail


urlpatterns = [
    path('', NewsList.as_view()),
    path('<int:pk>', OneNewsDetail.as_view()),
]

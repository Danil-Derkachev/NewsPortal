from django.urls import path
from django.contrib.auth.views import LoginView

from .views import BaseRegisterView, upgrade_me, logout_user

urlpatterns = [
    path('login', LoginView.as_view(template_name='sign/login.html'), name='login'),
    path('logout', logout_user, name='logout'),
    path('signup', BaseRegisterView.as_view(template_name='sign/signup.html'), name='signup'),
    path('upgrade', upgrade_me, name='upgrade')
]

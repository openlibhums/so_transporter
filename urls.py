from django.urls import re_path

from plugins.so_transporter import views


urlpatterns = [
    re_path(r'^manager/$', views.manager, name='so_transporter_manager'),
]

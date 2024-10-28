from . import views

from django.contrib import admin
from django.urls import path, include
from django.conf import settings


urlpatterns = [
  

    path('', views.order, name='index'),
    path('login/',views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    # path('started/', views.started, name='started'),
    path('register/', views.register, name='register'),
    path('chat/<int:order_id>/', views.chat, name='chat'),
    path('confirm/<str:id>/', views.confirm, name = 'confirm')

]
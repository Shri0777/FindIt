from django.urls import path

from . import views

app_name = 'items'

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('items/new/', views.item_create, name='item_create'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),
    path('items/<int:pk>/return/', views.mark_returned, name='mark_returned'),
]

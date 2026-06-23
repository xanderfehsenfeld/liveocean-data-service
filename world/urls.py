from django.urls import path
from . import views

urlpatterns = [
    path('forecast/drifters', views.worldborder_list, name='worldborder-list'),
    # path('worldborders/<int:pk>/', views.worldborder_detail, name='worldborder-detail'),
]

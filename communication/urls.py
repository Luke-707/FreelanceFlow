from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('<int:user_id>/', views.chat_detail, name='chat_detail'),
    path('call/<int:user_id>/', views.video_call, name='video_call'),
    path('api/unread-count/', views.unread_count, name='unread_count'),
]

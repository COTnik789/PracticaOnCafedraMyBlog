from django.urls import path
from . import views

app_name = 'blog'  # Пространство имён

urlpatterns = [
    path('', views.home, name='home'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('category/', views.category_list, name='category_list'),
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<int:pk>/update/', views.post_update, name='post_update'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('category/create/', views.category_create, name='category_create'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('manage-subscriptions/', views.manage_subscriptions, name='manage_subscriptions'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),  # Новый маршрут
]
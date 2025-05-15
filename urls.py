from django.urls import path
from . import views

app_name = 'additem'  # Add namespace

urlpatterns = [
    path('', views.home, name='home'),  # Add homepage URL
    path('additemform/', views.additemform, name='additemform'),
    path('additemconfirmation/', views.additemconfirmation, name='additemconfirmation'),
    path('staff/login/', views.staff_login, name='staff_login'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('register/', views.register, name='register'),  # Add register URL
    path('login/', views.login_view, name='login'),  # Add login URL
    path('logout/', views.logout_view, name='logout'),  # Add logout URL
] 


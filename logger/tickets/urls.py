from . import views
from django.urls import path

urlpatterns = [
    path('', views.landing, name='landing'),  # landing page
    path('create_ticket/', views.create_ticket, name='create_ticket'),
    path('manage_tickets/', views.manage_tickets, name='manage_tickets'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),

]
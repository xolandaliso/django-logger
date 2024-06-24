from . import views
from django.urls import path
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.login_view, name='landing'),  # landing page
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('home/', views.home, name='home'),
    path('create_ticket/', views.create_ticket, name='create_ticket'),
    path('create_manage/', views.create_manage, name='create_manage'),
    path('ticket_created/', views.ticket_created, name='ticket_created'),
    path('department_selection/', views.department_selection, name='department_selection'),
    path('department_ticket_creation/', views.department_ticket_creation, name='department_ticket_creation'),
    path('manage_tickets/', views.manage_tickets, name='manage_tickets'),
    path('ticket/<int:pk>/update/', views.ticket_update, name='ticket_update'),
    path('ticket/<int:pk>/delete/', views.ticket_delete, name='ticket_delete'),
    path('logout/', views.logout_view, name='logout'),

]

htmx_urlpatterns = [
    path('get_manage_tickets/', views.get_manage_tickets, name='get_manage_tickets'),
]

urlpatterns += htmx_urlpatterns
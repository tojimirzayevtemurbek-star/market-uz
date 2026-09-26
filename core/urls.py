from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('mijozlar/', views.customer_list_view, name='customer_list'),
    path('mijozlar/yangi/', views.customer_add_view, name='customer_add'),
    path('mijozlar/<int:pk>/', views.customer_detail_view, name='customer_detail'),
    path('qarz/<int:pk>/tolash/', views.debt_pay_view, name='debt_pay'),
    path('qarz/<int:pk>/ochirish/', views.debt_delete_view, name='debt_delete'),
    path('sozlamalar/', views.settings_view, name='settings'),
    path('sozlamalar/parol/', views.password_change_view, name='password_change'),
]

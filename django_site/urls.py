from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('api/', views.ApiView.as_view(), name='api'),
    path('fail2ban/', views.Fail2BanView.as_view(), name='fail2ban'),
    path('docs/', views.DocsView.as_view(), name='docs'),
    path('modules/', views.ModulesView.as_view(), name='modules'),
    path('plan/', views.PlanView.as_view(), name='plan'),
    path('crossref/', views.CrossRefView.as_view(), name='crossref'),
    path('login/', views.LoginView.as_view(), name='login'),
]

from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('login', views.LoginView.as_view(), name='login'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('logout', views.user_logout, name='logout'),
    path('checkotp', views.CheckOtp.as_view(), name='checkOtp'),
    path('forgot-password', views.ForgotPasswordView.as_view(), name='forgotPassword'),
]

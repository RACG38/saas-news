from django.urls import path
from .views import LoginView, RegisterView, CheckoutView, DashboardView, ForgotPasswordView, VerifyTokenView, ResetPasswordView, FeedbackView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    
    path('login/', LoginView.as_view(), name='login'),  
    path('register/', RegisterView.as_view(), name='register'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),  
    path('forgotpassword/', ForgotPasswordView.as_view(), name='forgotpassword'),
    path('verify-token/', VerifyTokenView.as_view(), name='verify-token'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('feedback/', FeedbackView.as_view(), name='feedback'),
   
]

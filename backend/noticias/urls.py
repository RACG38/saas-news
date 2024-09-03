from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),  # Rota correta
    path('register/', RegisterView.as_view(), name='register'),
    path('plans/', PlansView.as_view(), name='plans'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),  
    path('forgotpassword/', ForgotPasswordView.as_view(), name='forgotpassword'),
    path('verify-token/', VerifyTokenView.as_view(), name='verify-token'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

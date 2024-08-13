from django.urls import path
from .views import LoginView, RegisterView, PlansView

urlpatterns = [
    path('login/', LoginView.as_view(), name='entrar'),
    path('register/', RegisterView.as_view(), name='cadastro'),
    path('plans/', PlansView.as_view(), name='plans'),
       

]

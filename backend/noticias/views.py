from rest_framework import viewsets
from .models import Cliente, Plano
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
import stripe
from datetime import timedelta

stripe.api_key = 'sk_test_51Pn4lyFoYdflkG65qPLotl9dBgfaHOltbrQHlGXcyagLR8JpBTWpJIwSFmLgMI3rvRwBF1RmQ596z4ZvCCm1QhCg00rhjYHrvk'

def home(request):
    return render(request, 'home.html')


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            cliente = Cliente.objects.get(email=email)
            if check_password(password, cliente.password):
                return Response({"message": "Login bem-sucedido!"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Email ou senha incorretos."}, status=status.HTTP_401_UNAUTHORIZED)
        except Cliente.DoesNotExist:
            return Response({"message": "Email ou senha incorretos."}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    def post(self, request):
        try:
            nome = request.data.get('username')
            email = request.data.get('email')
            whatsapp = request.data.get('whatsapp')
            password = request.data.get('password')

            if not nome or not email or not password:
                raise ValidationError("Todos os campos são obrigatórios.")

            cliente_existente = Cliente.objects.filter(email=email).exists()

            if cliente_existente:
                return Response({"redirect": "login", "message": "Cliente já cadastrado. Redirecionando para o login."}, status=status.HTTP_200_OK)

            # Se o cliente não existir, prosseguir para a seleção de planos
            return Response({"redirect": "plans", "message": "Selecione um plano para concluir o cadastro."}, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"message": e.detail}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Erro inesperado: {e}")
            return Response({"message": "Erro interno do servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class PlansView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Capturar dados da requisição
            nome_plano = request.data.get('name')
            email = request.data.get('email')
            nome = request.data.get('username')
            whatsapp = request.data.get('whatsapp')
            password = request.data.get('password')
            action = request.data.get('action')
            amount = request.data.get('amount')

            # Verificar se todos os campos obrigatórios estão presentes
            if not nome or not email or not whatsapp or not password:
                raise ValidationError("Todos os campos são obrigatórios.")

            if action == 'create_payment_intent':
                return self.create_payment_intent(amount)

            elif action == 'confirm_payment':
                payment_intent_id = request.data.get('payment_intent_id')
                if not payment_intent_id:
                    return Response({'error': 'Payment Intent ID não fornecido.'}, status=status.HTTP_400_BAD_REQUEST)
                return self.confirm_payment(payment_intent_id, email, nome_plano, nome, whatsapp, password)

            else:
                return Response({'error': 'Ação inválida.'}, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Erro inesperado: {e}")
            return Response({"message": "Erro interno do servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_payment_intent(self, amount):
        try:
            if not amount:
                return Response({'error': 'Quantia não fornecida.'}, status=status.HTTP_400_BAD_REQUEST)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='brl',
                payment_method_types=['card'],
            )
            return Response({'client_secret': payment_intent['client_secret']}, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def confirm_payment(self, payment_intent_id, email, plano, nome, whatsapp, password):
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if payment_intent['status'] == 'succeeded':
                cliente, created = Cliente.objects.update_or_create(
                    email=email,
                    defaults={
                        'nome': nome,
                        'whatsapp': whatsapp,
                        'password': make_password(password),
                        'plano': plano,
                        'data_ultimo_pagamento': timezone.now() - timedelta(hours=3)
                    }
                )
                message = "Conta criada e pagamento confirmado!" if created else "Pagamento confirmado e dados atualizados!"
                return Response({'success': True, 'message': message, 'redirect': 'painel'}, status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'message': 'Pagamento não foi concluído.'})

        except stripe.error.StripeError as e:
            return Response({'success': False, 'message': str(e)})
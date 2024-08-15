from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Cliente, Plano, AcaoSelecionada
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
import json
from datetime import timedelta
import requests
from bs4 import BeautifulSoup
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken


stripe.api_key = 'sk_test_51Pn4lyFoYdflkG65qPLotl9dBgfaHOltbrQHlGXcyagLR8JpBTWpJIwSFmLgMI3rvRwBF1RmQ596z4ZvCCm1QhCg00rhjYHrvk'


class LoginView(APIView):
   
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            cliente = Cliente.objects.get(email=email)
            if check_password(password, cliente.password):
                return Response({
                    "message": "Login bem-sucedido!",
                    "cliente_id": cliente.id  # Retorne o ID do cliente
                }, status=status.HTTP_200_OK)
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
            plano_id = request.data.get('plano_id')
            email = request.data.get('email')
            nome = request.data.get('username')
            whatsapp = request.data.get('whatsapp')
            password = request.data.get('password')
            action = request.data.get('action')
            amount = request.data.get('amount')

            print(f"Dados recebidos: plano_id={plano_id}, email={email}, nome={nome}, whatsapp={whatsapp}, action={action}, amount={amount}")

            # Verificar se todos os campos obrigatórios estão presentes
            if not nome or not email or not whatsapp or not password:
                raise ValidationError("Todos os campos são obrigatórios.")

            # Verifique se o plano existe na base de dados pelo ID
            plano = Plano.objects.filter(id=plano_id).first()
            if not plano:
                print("Plano não encontrado.")
                return Response({'error': 'Plano não encontrado.'}, status=status.HTTP_400_BAD_REQUEST)

            print(f"Plano encontrado: {plano.nome_plano}")

            if plano.nome_plano == 'Freemium':
                return self.handle_freemium_plan(email, plano, nome, whatsapp, password)

            if action == 'create_payment_intent':
                print("Criando PaymentIntent.")
                return self.create_payment_intent(amount)

            elif action == 'confirm_payment':
                payment_intent_id = request.data.get('payment_intent_id')
                if not payment_intent_id:
                    print("Payment Intent ID não fornecido.")
                    return Response({'error': 'Payment Intent ID não fornecido.'}, status=status.HTTP_400_BAD_REQUEST)
                return self.confirm_payment(payment_intent_id, email, plano, nome, whatsapp, password)

            else:
                print("Ação inválida.")
                return Response({'error': 'Ação inválida.'}, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            print(f"Erro de validação: {str(e)}")
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            print(f"Erro Stripe: {str(e)}")
            return Response({"message": f"Erro no Stripe: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            print(f"Erro inesperado: {e}, tipo: {type(e)}")
            return Response({"message": f"Erro interno do servidor: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_payment_intent(self, amount):
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='brl',
                payment_method_types=['card'],
            )
            return Response({
                'client_secret': payment_intent['client_secret']
            }, status=status.HTTP_200_OK)
        except stripe.error.StripeError as e:
            print(f"Erro ao criar PaymentIntent: {str(e)}")
            return Response({"message": f"Erro ao criar PaymentIntent: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
                        'plano': plano,  # Aqui `plano` é uma instância do modelo `Plano` com base no ID
                        'data_ultimo_pagamento': timezone.now() - timedelta(hours=3)
                    }
                )
                message = "Conta criada e pagamento confirmado!" if created else "Pagamento confirmado e dados atualizados!"
                return Response({'success': True, 'message': message, 'redirect': 'painel'}, status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'message': 'Pagamento não foi concluído.'})

        except stripe.error.StripeError as e:
            print(f"Erro ao confirmar pagamento: {str(e)}")
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            print(f"Erro ao confirmar pagamento: {str(e)}, tipo: {type(e)}")
            return Response({'success': False, 'message': f"Erro inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DashboardView(APIView):

    def get(self, request):
        cliente_id = request.query_params.get('cliente_id')
        print(f"ID do cliente recebido: {cliente_id}")
        cliente = get_object_or_404(Cliente, id=cliente_id)

        # Buscar e processar dados do cliente e ações selecionadas
        dados_dashboard = {
            'cliente': {
                'nome': cliente.nome,
                'plano': {
                    'nome': cliente.plano.nome_plano,
                    'qtdade_ativos': cliente.plano.qtdade_ativos,
                    'qtdade_noticias': cliente.plano.qtdade_noticias,
                    'periodicidade': cliente.plano.periodicidade,
                    'email_opt': cliente.plano.email,
                    'whatsapp_opt': cliente.plano.whatsapp,
                    'temporeal': cliente.plano.tempo_real,

                },
                'data_ultimo_pagamento': cliente.data_ultimo_pagamento,
            },
            'acoes_selecionadas': list(cliente.acoes_selecionadas.values('simbolo')),
            'acoes_disponiveis': [],  # Placeholder para as ações obtidas de uma fonte externa
        }

        # Fazer a requisição ao site externo e obter a página HTML
        try:
            response = requests.get('https://www.dadosdemercado.com.br/acoes')
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            tabela = soup.find('table')  # Ajuste conforme necessário
            acoes_disponiveis = []

            for row in tabela.find_all('tr')[1:]:
                cols = row.find_all('td')
                simbolo = cols[0].text.strip()
                nome = cols[1].text.strip()
                acoes_disponiveis.append({'simbolo': simbolo, 'nome': nome})

        except requests.RequestException as e:
            return Response({"error": f"Erro ao buscar dados de ações: {str(e)}"}, status=400)
        except Exception as e:
            return Response({"error": f"Erro ao processar dados: {str(e)}"}, status=500)

        dados_dashboard['acoes_disponiveis'] = acoes_disponiveis
        return Response(dados_dashboard)

    def post(self, request):
        # Lógica de salvamento das ações selecionadas
        cliente_id = request.data.get('cliente_id')
        cliente = get_object_or_404(Cliente, id=cliente_id)
        acoes = request.data.get('selectedStocks', [])

        if len(cliente_id) == 0:

            for acao_data in acoes:
                AcaoSelecionada.objects.create(
                    cliente=cliente,
                    simbolo=acao_data['simbolo'],
                    defaults={'nome': acao_data['nome']}
            )

        else:

            for acao_data in acoes:
                AcaoSelecionada.objects.update(
                    cliente=cliente,
                    simbolo=acao_data['simbolo'],
                    defaults={'nome': acao_data['nome']}
            )

        return Response({"message": "Ações atualizadas com sucesso!"})
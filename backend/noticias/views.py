from .libs import *
from django.conf import settings
import logging

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger('my_custom_logger')

logger.setLevel(logging.DEBUG)

# Função para enviar o e-mail de confirmação
def enviar_email_confirmacao(cliente, dados_pagamento):

    if cliente.data_ultimo_pagamento == timezone.now().date():
        email_template = 'email/welcome.html'
        subject = f'{cliente.nome}, bem-vindo(a) ao Nosso Serviço!'
    else:
        email_template = 'email/renewal.html'
        subject = f'{cliente.nome}, sua renovação de Assinatura foi Concluída'
  
    # Contexto para o e-mail
    email_context = {
        'cliente': cliente,
        'plano': cliente.plano,
        'valor_plano': cliente.plano.valor,  # Supondo que 'valor' seja o atributo que contém o preço do plano
        'data_renovacao_pagamento': (timezone.now().date() + timezone.timedelta(days=30)).strftime('%m/%Y'),
        'numero_cartao': dados_pagamento.get('card').get('last4'),
        'data_vencimento':  f"{dados_pagamento.get('card').get('exp_month'):02d}/{str(dados_pagamento.get('card').get('exp_year'))[-2:]}",  # MM/YY
    }

    # Renderizar a mensagem HTML
    html_message = render_to_string(email_template, email_context)
    plain_message = strip_tags(html_message)

    # Enviar o e-mail
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [cliente.email],
        html_message=html_message,
        fail_silently=False,
    )    

    logger.debug(f"E-mail enviado ao cliente {cliente.email}")
    

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
        
class DashboardView(APIView):

    def get(self, request):
        cliente_id = request.query_params.get('cliente_id')
        print(f"ID do cliente recebido: {cliente_id}")
        cliente = get_object_or_404(Cliente, id=cliente_id)

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
            'acoes_selecionadas': list(cliente.acoes_selecionadas.values('simbolo', 'nome')),
            'acoes_disponiveis': [],  # Placeholder para as ações obtidas de uma fonte externa
        }

        try:
            response = requests.get('https://www.dadosdemercado.com.br/acoes')
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            tabela = soup.find('table')
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
        cliente_id = request.data.get('userId')
        cliente = get_object_or_404(Cliente, id=cliente_id)
        acoes = request.data.get('selectedStocks', [])

        # Apagar as ações não selecionadas antes de atualizar
        AcaoSelecionada.objects.filter(cliente=cliente).exclude(simbolo__in=[acao['simbolo'] for acao in acoes]).delete()

        for acao_data in acoes:
            # Tentar atualizar se a ação já existe, caso contrário, criar uma nova entrada
            AcaoSelecionada.objects.update_or_create(
                cliente=cliente,
                simbolo=acao_data['simbolo'],
                defaults={'nome': acao_data['nome']}
            )

        return Response({"message": "Ações atualizadas com sucesso!"}, status=status.HTTP_200_OK)

class PlansView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            plano_id = request.data.get('plano_id')
            email = request.data.get('email')
            nome = request.data.get('username')
            whatsapp = request.data.get('whatsapp')
            password = request.data.get('password')
            action = request.data.get('action')
            payment_method = request.data.get('payment_method')

            # Tentar recuperar o cliente do banco de dados
            cliente, created = Cliente.objects.get_or_create(
                email=email,
                defaults={
                    'nome': nome,
                    'whatsapp': whatsapp,
                    'password': make_password(password),
                    'data_ultimo_pagamento': timezone.now(),
                }
            )  

            if created:
                # Criar o cliente no Stripe
                customer = stripe.Customer.create(
                    email=email,
                    name=nome,
                    description='Cliente registrado para pagamentos recorrentes',
                    metadata={
                        'whatsapp': whatsapp,
                    }
                )                

                # Atualizar o cliente local com o ID do Stripe
                cliente.stripe_customer_id = customer.id
                cliente.save()

            else:
                # Se o cliente já existia, recuperar o ID do cliente Stripe
                cliente = get_object_or_404(Cliente, email=email)       

            if action == 'create_payment_intent':
                return Response({'message': 'Pagamento único não suportado para planos de assinatura.'}, status=status.HTTP_400_BAD_REQUEST)

            elif action == 'confirm_payment':
                response = self.confirm_payment(request)

                if response.status_code == 200:
                    # Chamada para enviar o e-mail após confirmação bem-sucedida do pagamento
                    enviar_email_confirmacao(cliente, payment_method)

                return response

            else:
                return Response({'error': 'Ação inválida.'}, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            return Response({"message": f"Erro no Stripe: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"message": f"Erro interno do servidor: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def confirm_payment(self, request):
        try:
            # Acessando os dados enviados pelo frontend
            payment_method = request.data.get('payment_method')
            email = request.data.get('email')
            plano_id = request.data.get('plano_id')

            plano = get_object_or_404(Plano, id=plano_id)

            # Recupera ou cria um cliente no banco de dados
            cliente, created = Cliente.objects.update_or_create(
                email=email,
                defaults={
                    'plano': plano,
                    'data_ultimo_pagamento': timezone.now(),
                }
            )

            # Anexar o PaymentMethod ao cliente no Stripe, se ainda não estiver anexado
            stripe.PaymentMethod.attach(
                payment_method.get('id'),
                customer=cliente.stripe_customer_id,
            )

            # Definir o PaymentMethod como padrão para o cliente
            stripe.Customer.modify(
                cliente.stripe_customer_id,
                invoice_settings={'default_payment_method': payment_method.get('id')},
            )

            # Verificar se o cliente já possui uma assinatura ativa
            existing_subscriptions = stripe.Subscription.list(customer=cliente.stripe_customer_id, status='active')

            if existing_subscriptions.data:
                # Cancelar a assinatura existente
                for subscription in existing_subscriptions.data:
                    stripe.Subscription.delete(subscription.id)

            # Escolher o Price ID baseado no plano
            if plano_id == 1:  # Plano Freemium
                price_id = "price_1Pr8HTFoYdflkG65IgNczpqo"
            elif plano_id == 2:  # Plano Basic
                price_id = "price_1PqRMXFoYdflkG65i6tWga0K"
            else:  # Plano Pro
                price_id = "price_1PqRMwFoYdflkG65l1ac87Hd"

            # Criar a nova assinatura no Stripe
            subscription = stripe.Subscription.create(
                customer=cliente.stripe_customer_id,
                items=[{'price': price_id}],
                default_payment_method=payment_method.get('id'),
                expand=['latest_invoice.payment_intent'],
            )

            # Critérios de pesquisa: Usamos o cliente como chave de pesquisa
            # lookup_criteria = {'cliente': cliente}

            # # Campos a serem atualizados ou criados se o registro não existir
            # defaults_data = {
            #     'numero_cartao': payment_method.get('card').get('last4'),
            #     'data_vencimento': f"{payment_method.get('card').get('exp_month')}/{str(payment_method.get('card').get('exp_year'))[-2:]}",  # MM/YY
            #     'cep': payment_method.get('billing_details').get('address').get('postal_code'),
            #     'data_renovacao_pagamento': timezone.now().date() + timezone.timedelta(days=30),
            # }

            # # Usando update_or_create para atualizar ou criar o registro
            # dados_pagamento, created = DadosPagamento.objects.update_or_create(
            #     **lookup_criteria,
            #     defaults=defaults_data,
            # )

            return Response({
                'success': True,
                'message': "Pagamento e assinatura confirmados com sucesso!",
                # 'subscription_id': subscription.id,
            }, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': f"Erro inesperado ao atualizar o usuário: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

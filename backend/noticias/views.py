from .libs import *
from django.conf import settings
import logging

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger('my_custom_logger')

logger.setLevel(logging.DEBUG)

def enviar_email_feedback(nome, email, mensagem):
    subject = f'Feedback recebido de {nome}'
    
    # Contexto para o e-mail
    email_context = {
        'nome': nome,
        'email': email,
        'mensagem': mensagem,
    }
    
    # Renderizar a mensagem HTML
    email_template = 'email/feedback.html'
    html_message = render_to_string(email_template, email_context)
    plain_message = strip_tags(html_message)
    
    # Enviar o e-mail
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        ['renan.acg7@gmail.com'],  # E-mail de destino
        html_message=html_message,
        fail_silently=False,
    )

def enviar_email_free(cliente, change_plan_flag):

    email_template = 'email/welcome_free.html'

    if change_plan_flag == True:

        # email_template = 'email/change_plan.html'
        subject = f'{cliente.nome}, a mudança do seu plano foi concluída'

    else:

        subject = f'{cliente.nome}, bem-vindo(a) ao Plano Free!'    

    # Contexto para o e-mail
    email_context = {
        'cliente': cliente,
        'plano': cliente.plano,
        'valor_plano': cliente.plano.valor,             
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

def enviar_email_reset_token(cliente, token_obj):

    email_template = 'email/change_password.html'
    subject = f'{cliente.nome}, esse é o seu pedido de recuperação de senha'     

    email_context = {
        'cliente': cliente,
        'token_id': token_obj.token_id,
        'data_criacao': token_obj.data_criacao,     
        'data_expiracao': token_obj.data_expiracao,        
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

def enviar_email_confirmacao(cliente, payment_method, changeplan_flag):

    delta = datetime.today().date() - cliente.data_ultimo_pagamento

    if changeplan_flag == True:
        email_template = 'email/change_plan.html'
        subject = f'{cliente.nome}, a mudança do seu plano foi concluída'


    elif delta.days < 1:        
        email_template = 'email/welcome.html'
        subject = f'{cliente.nome}, bem-vindo(a) ao Nosso Serviço!'

    else:
        email_template = 'email/renewal.html'
        subject = f'{cliente.nome}, sua renovação do Plano {cliente.plano} foi efetuada'

    # Contexto para o e-mail
    email_context = {
        'cliente': cliente,
        'plano': cliente.plano,
        'valor_plano': cliente.plano.valor,  
        'data_renovacao_pagamento': (timezone.now().date() + timezone.timedelta(days=30)).strftime('%m/%Y'),
        'numero_cartao': payment_method.get('card').get('last4'),
        'data_vencimento':  f"{payment_method.get('card').get('exp_month'):02d}/{str(payment_method.get('card').get('exp_year'))[-2:]}",  # MM/YY
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

class ForgotPasswordView(APIView):

    def post(self, request):

        email = request.data.get('email')
        cliente = get_object_or_404(Cliente, email=email)
        
        token_obj = cliente.token        

        enviar_email_reset_token(cliente, token_obj)

        return Response({"message": "Instruções de redefinição de senha enviadas para o seu email."}, status=status.HTTP_200_OK)

class VerifyTokenView(APIView):

    def post(self, request):

        token = request.data.get('token') 
       
        try:
            
            token_obj = Token.objects.get(token_id=token)
            cliente = Cliente.objects.get(token=token_obj)

            if timezone.now() > token_obj.data_expiracao:

                token_obj, _ = Token.objects.update_or_create(
                    cliente=cliente,
                    defaults={
                        'token_id': ''.join(random.choices(string.digits, k=6)),                       
                    }
                )      

                enviar_email_reset_token(cliente, token_obj)

                return Response({"message": "Token expirado"}, status=status.HTTP_400_BAD_REQUEST) # Reenvia o token por email               

            
            token_obj, _ = Token.objects.update_or_create(
            cliente=cliente,
            defaults={
                'token_id': token_obj.token_id,
                'data_criacao': timezone.now(),  # Subtrai 3 horas da data de criação
                'data_expiracao': timezone.now() + timedelta(hours=1)  # Token expira em 1 hora, mas subtraindo 3 horas resulta em 2 horas a partir de agora
            }
        )  

            return Response({"message": "Token válido"}, status=status.HTTP_200_OK)

        except Token.DoesNotExist:
            return Response({"message": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):

    def post(self, request, *args, **kwargs):

        try:

            token = str(request.data.get('token'))             
            password = request.data.get('password')    

            token_obj = Token.objects.get(token_id=token)  # Supondo que 'token_string' seja o token que você quer buscar
            cliente = Cliente.objects.get(token=token_obj)  # Busca o cliente associado ao token
        
            if not token or not password:
                return Response({'message': 'Token e senha são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)
            else:

                cliente.password = make_password(password) # Atualizar o cliente local com o ID do Stripe
                cliente.save()
                return Response({'message': 'Senha redefinida com sucesso.'}, status=status.HTTP_200_OK)               
                
        except ObjectDoesNotExist:
            return Response({'message': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': f'Ocorreu um erro: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
   
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        plano = request.data.get('plano_nome')

        try:
            cliente = Cliente.objects.get(email=email)

            if plano == "Free":

                # Verificar se o cliente já possui uma assinatura ativa
                existing_subscriptions = stripe.Subscription.list(customer=cliente.stripe_customer_id, status='active')

                if existing_subscriptions.data:
                    # Cancelar a assinatura existente
                    for subscription in existing_subscriptions.data:
                        stripe.Subscription.delete(subscription.id)  

                # Atualizar o plano do cliente para o plano "Free"
                cliente.plano = Plano.objects.get(nome_plano='Free')
                cliente.data_ultimo_pagamento = timezone.now()
                cliente.save()  

                enviar_email_free(cliente, True) 
                
        
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

            plan_id = request.data.get('plan_id')                       
            action = request.data.get('action')
            email = request.data.get('email')                               
            nome = request.data.get('nome')                    
            whatsapp = request.data.get('whatsapp')            
            password = request.data.get('password')                 
            change_plan = request.data.get('change_plan') 
                 

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
                   

            if created: # Verifica se é primeiro acesso

                cliente.tickers.clear() # Inicializa os tickers como um campo vazio

                # Tentar recuperar o cliente pelo email
                customer_stripe = stripe.Customer.list(email=email)
                
                if customer_stripe.data:
                    
                    customer = customer_stripe.data[0]

                else:

                    # Criar o cliente no Stripe
                    customer = stripe.Customer.create(
                        email=email,
                        name=nome,
                        description='Cliente registrado para pagamentos recorrentes',
                        metadata={
                            'whatsapp': whatsapp,
                        }
                    )   

            if cliente: # Verifica se o cliente existe no banco de dados

                if action == 'get_current_plan':    

                    return JsonResponse({
                        'plan_id': cliente.plano.id,                
                    })                                 


                customer = stripe.Customer.list(email=email).data[0] # Verifica se já existe um cadastro do cliente no Stripe
                cliente.stripe_customer_id = customer.id # Atualizar o cliente local com o ID do Stripe
                cliente.save()      

                
                if plan_id == 1:                    

                    # Criar ou atualizar o token de redefinição de senha no banco de dados
                    token_obj, created = Token.objects.update_or_create(
                        cliente=cliente,
                        defaults={
                            'token_id': ''.join(random.choices(string.digits, k=6)),  # Gera uma string de 6 dígitos
                            'data_criacao': timezone.now(),  # Subtrai 3 horas da data de criação
                            'data_expiracao': timezone.now() + timedelta(hours=1)
                        }
                    ) 

                    # Atualiza o plano do cliente para o Free
                    cliente, _ = Cliente.objects.update_or_create(
                        email=email,
                            defaults={
                                'plano': get_object_or_404(Plano, id=plan_id),
                                'data_ultimo_pagamento': timezone.now(),
                                'token': token_obj
                                
                                }                      

                    )                        

                    # Verifica se o cliente já possui uma assinatura ativa. Se tiver, irá ser cancelada
                    existing_subscriptions = stripe.Subscription.list(customer=customer.id, status='active')
                    
                    if existing_subscriptions.data:
                        
                        for subscription in existing_subscriptions.data:
                            stripe.Subscription.delete(subscription.id) # Cancelar a assinatura existente

                    enviar_email_free(cliente, change_plan)
                
                    return Response({
                    'success': True,
                    'message': "Cliente cadastrado no plano Free",
                
                }, status=status.HTTP_200_OK)  
                else:

                    return Response({
                        'success': True,
                        'message': "Cliente cadastrado banco de dados",

                    }, status=status.HTTP_200_OK)         
                                 

        except ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            return Response({"message": f"Erro no Stripe: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"message": f"Erro interno do servidor: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            

class CheckoutView(APIView):

    def get_card_info(self, request):

        try:

            email = request.data.get('email')      

            customer_stripe = stripe.Customer.list(email=email)

            # Verifique se o cliente existe
            cliente = Cliente.objects.filter(email=email).first()
            
            if not cliente:
                return Response({'success': False, 'error': 'Cliente não encontrado'}, status=status.HTTP_404_NOT_FOUND)
                
            if customer_stripe.data:
                
                customer = customer_stripe.data[0]    

            # Busca os métodos de pagamento do cliente no Stripe
            payment_methods = stripe.PaymentMethod.list(
                customer=customer.id,
                type="card"
            )

            cards = []
            for pm in payment_methods.data:
                card = pm.card
                cards.append({
                    'id': pm.id,
                    'brand': card.brand,
                    'last4': card.last4,
                    'exp_month': card.exp_month,
                    'exp_year': card.exp_year,
                })

            if cards:
                return Response({
                    'success': True,
                    'cards': cards,
                    'cpf': cliente.cpf,
                    'cep': cliente.endereco.cep,
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Nenhum cartão encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        except stripe.error.StripeError as e:
            return Response({"message": f"Erro no Stripe: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"message": f"Erro interno do servidor: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            # Acessando os dados enviados pelo frontend
            payment_method = request.data.get('payment_method')
            email = request.data.get('email')
            plan_id = request.data.get('plan_id')
            change_plan = request.data.get('change_plan_flag')
            cpf = request.data.get('cpf')
            address_data = request.data.get('address')
            action = request.data.get('action')

            # Quando a ação é obter informações de cartão
            if action == "get_card_info":
                return self.get_card_info(request)

            # Acessa os dados do endereço
            if address_data:
                logradouro = address_data.get('logradouro')
                numero = address_data.get('numero')
                complemento = address_data.get('complemento')
                cidade = address_data.get('cidade')
                bairro = address_data.get('bairro')
                estado = address_data.get('estado')
                cep = address_data.get('cep')

            # Recupera o plano
            plano = get_object_or_404(Plano, id=plan_id)

            # Escolhe o Price ID baseado no plano
            if plan_id == 2:
                price_id = "price_1PqRMXFoYdflkG65i6tWga0K"  # Plano Basic
            else:
                price_id = "price_1PqRMwFoYdflkG65l1ac87Hd"  # Plano Pro

            if email and plano:
                # Recupera ou cria o cliente no banco de dados
                cliente, _ = Cliente.objects.update_or_create(
                    email=email,
                    defaults={
                        'plano': plano,
                        'data_ultimo_pagamento': timezone.now(),
                    }
                )

            # Criar ou atualizar o token no banco de dados
            token_obj, created = Token.objects.update_or_create(
                cliente=cliente,
                defaults={
                    'token_id': ''.join(random.choices(string.digits, k=6)),  # Gera uma string de 6 dígitos
                    'data_criacao': timezone.now(),
                    'data_expiracao': timezone.now() + timedelta(hours=1)
                }
            )

            if cpf:

                cliente.cpf = cpf
                
            cliente.token = token_obj
            cliente.save()

            # Atualiza ou cria o endereço
            endereco, created = Endereco.objects.update_or_create(
                cep=cep,  
                defaults={
                    'logradouro': logradouro,
                    'numero': numero,
                    'complemento': complemento,
                    'cidade': cidade,
                    'bairro': bairro,
                    'estado': estado,
                }
            )

            if endereco:
                
                cliente.endereco = endereco
                cliente.save()

            # Verifica se é um método de pagamento salvo (tem um 'id' presente)
            if 'id' in payment_method:
                payment_method_id = payment_method['id']
                
                # Verifica se o PaymentMethod já está anexado ao cliente
                payment_method_obj = stripe.PaymentMethod.retrieve(payment_method_id)
                if not payment_method_obj.customer:
                    # Anexa o PaymentMethod ao cliente no Stripe
                    stripe.PaymentMethod.attach(payment_method_id, customer=cliente.stripe_customer_id)
            else:
                # Se for um novo PaymentMethod
                new_payment_method_fingerprint = payment_method.get('card', {}).get('fingerprint')
                existing_payment_methods = stripe.PaymentMethod.list(
                    customer=cliente.stripe_customer_id,
                    type="card"
                )

                method_exists = False
                for method in existing_payment_methods.data:
                    if method.card.fingerprint == new_payment_method_fingerprint:
                        method_exists = True
                        payment_method_id = method.id
                        break

                if not method_exists:
                    payment_method_id = payment_method.get('id')
                    stripe.PaymentMethod.attach(payment_method_id, customer=cliente.stripe_customer_id)

            # Define o PaymentMethod como padrão para o cliente
            stripe.Customer.modify(
                cliente.stripe_customer_id,
                invoice_settings={'default_payment_method': payment_method_id},
            )

            # Verificar se o cliente já possui uma assinatura ativa
            existing_subscriptions = stripe.Subscription.list(customer=cliente.stripe_customer_id, status='active')

            if existing_subscriptions.data:
                # Cancelar a assinatura existente
                for subscription in existing_subscriptions.data:
                    stripe.Subscription.delete(subscription.id)

            # Criar a nova assinatura no Stripe
            subscription = stripe.Subscription.create(
                customer=cliente.stripe_customer_id,
                items=[{'price': price_id}],
                default_payment_method=payment_method_id,
                expand=['latest_invoice.payment_intent'],
            )

            cliente.refresh_from_db()

            # Enviar e-mail de confirmação
            enviar_email_confirmacao(cliente, payment_method, change_plan)

            return Response({
                'success': True,
                'message': "Pagamento e assinatura confirmados com sucesso!",
            }, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return Response({'error': f"Erro inesperado ao atualizar o usuário: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DashboardView(APIView):

    def get(self, request):
        cliente_id = request.query_params.get('cliente_id')
        cliente = get_object_or_404(Cliente, id=cliente_id)

        dados_dashboard = {
            'cliente': {
                'nome': cliente.nome,
                'email': cliente.email,
                'whatsapp': cliente.whatsapp,
                'password': cliente.password,
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
            'acoes_selecionadas': list(cliente.tickers.values('simbolo', 'nome')),
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
                volume = cols[2].text.strip()

                # Remover pontos e converter o volume para um número (float)
                volume = volume.replace('.', '').replace(',', '.')
                try:
                    volume = float(volume)  # Conversão para float
                except ValueError:
                    volume = 0  # Caso haja erro na conversão, define como 0

                acoes_disponiveis.append({'simbolo': simbolo, 'nome': nome, 'volume': volume})

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

        # Limpar todos os tickers atuais do cliente antes de adicionar os novos
        cliente.tickers.clear()

        for acao_data in acoes:

            acao_selecionada, created = AcaoSelecionada.objects.update_or_create(
                simbolo=acao_data['simbolo'],
                defaults={'nome': acao_data['nome']}
            )
            cliente.tickers.add(acao_selecionada)

        cliente.save()

        return Response({"message": "Ações atualizadas com sucesso!"}, status=status.HTTP_200_OK)

    def delete(self, request):

        data = json.loads(request.body)
        email = data.get('email')  

        try:
            cliente = Cliente.objects.get(email=email)              
            
            # Verificar se o cliente já possui uma assinatura ativa
            existing_subscriptions = stripe.Subscription.list(customer=cliente.stripe_customer_id, status='active')

            if existing_subscriptions.data:
                # Cancelar a assinatura existente
                for subscription in existing_subscriptions.data:
                    stripe.Subscription.delete(subscription.id)       
            
            # Excluir o usuário do banco de dados
            cliente.delete()

            return JsonResponse({'status': 'success', 'message': 'Assinatura cancelada e usuário excluído com sucesso.'})
        except Cliente.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Usuário não encontrado.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

class FeedbackView(APIView):

    def post(self, request, *args, **kwargs):

        try:
            data = request.data  
            nome = data.get('nome')
            email = data.get('email')
            mensagem = data.get('mensagem')

            if nome and email and mensagem:
                # Chama a função para enviar o email de feedback
                enviar_email_feedback(nome, email, mensagem)
                return Response({'message': 'Feedback enviado com sucesso!'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Todos os campos são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
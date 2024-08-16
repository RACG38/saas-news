from .libs import *


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


            # Verificar se o plano existe na base de dados pelo ID
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
                payment_method_id = request.data.get('payment_method_id')
                
                if not payment_intent_id or not payment_method_id:
                    print("Payment Intent ID ou Payment Method ID não fornecido.")
                    return Response({'error': 'Payment Intent ID ou Payment Method ID não fornecido.'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Chamar confirm_payment com os IDs corretos
                return self.confirm_payment(payment_intent_id, payment_method_id, email, plano, nome, whatsapp, password)

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

    def confirm_payment(self, payment_intent_id, payment_method_id, email, plano, nome, whatsapp, password):
        try:
            # Recuperar detalhes completos do payment_method usando o ID correto
            payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
            card_details = payment_method.card
            
            # Salvar ou atualizar as informações do cliente
            cliente, created = Cliente.objects.update_or_create(
                email=email,
                defaults={
                    'nome': nome,
                    'whatsapp': whatsapp,
                    'password': password,  # Aqui você pode usar make_password para hashear a senha se necessário
                    'plano': plano,
                    'data_ultimo_pagamento': timezone.now(),
                }
            )

            # Salvar os detalhes do pagamento e agendar a próxima renovação
            dados_pagamento = DadosPagamento.objects.create(
                cliente=cliente,
                numero_cartao=card_details.last4,  # Armazena os últimos 4 dígitos do cartão
                data_vencimento=f"{card_details.exp_month}/{str(card_details.exp_year)[-2:]}",  # MM/YY
                cep=payment_method.billing_details.address.postal_code if payment_method.billing_details.address else '',
                data_renovacao_plano=timezone.now().date() + timezone.timedelta(days=30)
            )

            # Enviar e-mail de boas-vindas ou de renovação
            if created:
                subject = f'{cliente.nome}, bem-vindo(a) ao Nosso Serviço!'
                html_message = render_to_string('email/welcome.html', {'cliente': cliente, 'plano': plano, 'dados_pagamento': dados_pagamento})
                plain_message = strip_tags(html_message)
            else:
                subject = f'{cliente.nome}, sua renovação de Assinatura foi Concluída'
                html_message = render_to_string('email/renewal.html', {'cliente': cliente, 'plano': plano, 'dados_pagamento': dados_pagamento})
                plain_message = strip_tags(html_message)

            send_mail(
                subject,
                plain_message,
                'renan.acg7@gmail.com',  # Substitua pelo seu endereço de e-mail configurado
                [cliente.email],
                html_message=html_message,
                fail_silently=False,
            )

            message = "Conta criada e pagamento confirmado!" if created else "Pagamento confirmado e dados atualizados!"
            return Response({'success': True, 'message': message}, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'success': False, 'message': f"Erro inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
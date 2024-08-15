import React from 'react';
import { CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const CheckoutForm = ({ selectedPlan, userEmail, userName, userWhatsapp, userPassword, navigate }) => {
    const stripe = useStripe();
    const elements = useElements();

    const handleSubmit = async (event) => {
        event.preventDefault();

        if (!stripe || !elements) {
            console.error('Stripe.js ainda não foi carregado.');
            return;
        }

        try {
            // Criar PaymentIntent no backend
            const paymentIntentResponse = await fetch('http://localhost:8000/auth/plans/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    plano_id: selectedPlan.plan_id,
                    email: userEmail,
                    username: userName,
                    whatsapp: userWhatsapp,
                    password: userPassword,
                    amount: parseFloat(selectedPlan.price.replace('R$', '').replace(',', '.')) * 100, // Convertendo para centavos
                    action: 'create_payment_intent', // Ação para distinguir o tipo de requisição
                }),
            });

            if (!paymentIntentResponse.ok) {
                const paymentIntentData = await paymentIntentResponse.json();
                throw new Error(paymentIntentData.message);
            }

            const { client_secret: clientSecret } = await paymentIntentResponse.json();

            // Confirmar o pagamento com o Stripe
            const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: elements.getElement(CardElement),
                    billing_details: {
                        email: userEmail,
                    },
                },
            });

            if (error) {
                console.error('Erro ao confirmar o pagamento:', error.message);
                return;
            }

            if (paymentIntent.status === 'succeeded') {
                console.log('Pagamento bem-sucedido, atualizando usuário:', {
                    name: selectedPlan.plan_name,
                    email: userEmail,
                    username: userName,
                    whatsapp: userWhatsapp,
                    password: userPassword,
                    payment_intent_id: paymentIntent.id,
                });

                const updateUserResponse = await fetch('http://localhost:8000/auth/plans/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        plano_id: selectedPlan.plan_id,
                        email: userEmail,
                        username: userName,
                        whatsapp: userWhatsapp,
                        password: userPassword,
                        payment_intent_id: paymentIntent.id,
                        action: 'confirm_payment', // Ação para confirmar o pagamento e atualizar o usuário
                    }),
                });

                if (!updateUserResponse.ok) {
                    const updateUserData = await updateUserResponse.json();
                    throw new Error(updateUserData.message);
                }

                console.log('Usuário criado ou atualizado:', await updateUserResponse.json());
                navigate('/login');
            }
        } catch (error) {
            console.error('Erro no processo de pagamento:', error.message);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <CardElement />
            <button type="submit" disabled={!stripe}>
                Pagar {selectedPlan.price}
            </button>
        </form>
    );
};

export default CheckoutForm;

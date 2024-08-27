import React, { useState } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { useNavigate } from 'react-router-dom';

const stripePromise = loadStripe('pk_test_51Pn4lyFoYdflkG65WPti0iFUvKpCaTa4xSoGu9Zu2JvIAwbKhHfA73F9b2cO7DddKbrF6PXE05IXQ5o8DqFvQwE1007moBnRIJ');  // Substitua com sua chave publicável do Stripe

const CheckoutForm = ({ selectedPlan, userEmail, userName, userWhatsapp, userPassword, onPaymentResult, change_plan }) => {
    const stripe = useStripe();
    const elements = useElements();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);

        if (!stripe || !elements) {
            setLoading(false);
            return;
        }

        const cardElement = elements.getElement(CardElement);

        // 1. Crie o PaymentMethod no frontend
        const { error: paymentMethodError, paymentMethod } = await stripe.createPaymentMethod({
            type: 'card',
            card: cardElement,
            billing_details: {
                email: userEmail,
            },
        });

        if (paymentMethodError) {
            console.error('Erro ao criar PaymentMethod:', paymentMethodError.message);
            onPaymentResult('error');
            setLoading(false);
            return;
        }

        console.log('PaymentMethod criado com sucesso:', paymentMethod);

        // 2. Envie o PaymentMethod ID para o backend para criar a assinatura
        try {
            const response = await fetch('http://localhost:8000/auth/plans/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    plan_id: selectedPlan.plan_id,
                    email: userEmail,
                    nome: userName,
                    whatsapp: userWhatsapp,
                    password: userPassword,
                    action: 'confirm_payment',  // Usar a ação confirm_payment para criar a assinatura
                    payment_method: paymentMethod,
                    change_plan: change_plan,
                    
                }),
            });

            const data = await response.json();

            if (data.success) {
                console.log('Assinatura criada com sucesso:', data.subscription_id);
                onPaymentResult('success');

                // Navegar para a tela de login após o sucesso
                setTimeout(() => {
                    navigate('/login');
                }, 5000);  // Adiciona um delay de 5 segundos

            } else {
                console.error('Erro ao criar a assinatura no backend:', data.error);
                onPaymentResult('error');
            }
            

        } catch (error) {
            console.error('Erro ao processar a assinatura:', error.message);
            onPaymentResult('error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <CardElement />
            <button type="submit" disabled={!stripe || loading}>
                {loading ? <div className="spinner"></div> : `Pagar ${selectedPlan.price}`}
            </button>
            {loading && (
                <p className="loading-text">Estamos validando o seu pagamento... só vai levar mais alguns segundos.</p>
            )}
        </form>
    );
};

const Checkout = (props) => (
    <Elements stripe={stripePromise}>
        <CheckoutForm {...props} />
    </Elements>
);

export default Checkout;
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStripe, useElements, CardElement } from '@stripe/react-stripe-js';
import '../styles/CheckoutForm.css';

const CheckoutForm = ({ selectedPlan, userEmail, userName, userWhatsapp, userPassword, onPaymentResult, onPaymentStart, change_plan, currentPlanId }) => {
    const stripe = useStripe();
    const elements = useElements();
    const [loading, setLoading] = useState(false);
    const [cards, setCards] = useState([]);
    const [selectedCard, setSelectedCard] = useState('new');
    const [showPopup, setShowPopup] = useState(false);
    const [isCloseDisabled, setIsCloseDisabled] = useState(false);

    const navigate = useNavigate();

    useEffect(() => {
        const fetchCardInfo = async () => {
            try {
                const response = await fetch('http://localhost:8000/auth/plans/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        email: userEmail,
                        action: 'get_card_info' // Ação para buscar os cartões salvos
                    }),
                });

                const data = await response.json();                 

                if (data.success) {
                    setCards(data.cards);
                } else {
                    console.error('Erro ao buscar informações do cartão:', data.error);
                }
            } catch (error) {
                console.error('Erro ao buscar informações do cartão:', error.message);
            }
        };

        fetchCardInfo();
    }, [userEmail]);

    const handleCardSelect = (cardId) => {
        setSelectedCard(cardId);
    };  

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        onPaymentStart();
        
        if (!stripe || !elements) {
            setLoading(false);
            setIsCloseDisabled(false);
            return;
        }
    
        let paymentMethod;
    
        if (selectedCard !== 'new') {
            paymentMethod = cards.find(card => card.id === selectedCard);
        } else {
            const cardElement = elements.getElement(CardElement);
            const { error: paymentMethodError, paymentMethod: newPaymentMethod } = await stripe.createPaymentMethod({
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
                setIsCloseDisabled(false);
                return;
            }
    
            paymentMethod = newPaymentMethod;
        }        
    
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
                    action: 'confirm_payment',
                    payment_method: paymentMethod,  
                    change_plan: change_plan,
                }),                
            });
    
            const data = await response.json();

            if (data.success) {
                console.log('Assinatura criada com sucesso:', data.subscription_id);
                onPaymentResult('success');
                setTimeout(() => {
                    navigate('/login');
                }, 2000);
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
        <div>
            {showPopup && (
                <div className="popup">
                    <p>Você já possui este plano. Selecione um plano diferente.</p>
                    <button onClick={() => setShowPopup(false)}>
                        Fechar
                    </button>
                </div>
            )}

            <form onSubmit={handleSubmit}>
                <h3>Plano Selecionado: {selectedPlan.plan_name}</h3>
                <p>Preço: {selectedPlan.price}</p>
                {cards.length > 0 && (
                    <div className="card-selection">
                        <p><strong>Selecione um cartão cadastrado ou insira um novo:</strong></p>
                        {cards.map((card) => (
                            <div
                                key={card.id}
                                className={`card-option ${selectedCard === card.id ? 'selected' : ''}`}
                                onClick={() => handleCardSelect(card.id)}
                            >
                                {card.brand.toUpperCase()} **** **** **** {card.last4} (Válido até {card.exp_month}/{card.exp_year})
                            </div>
                        ))}
                        <div
                            className={`card-option ${selectedCard === 'new' ? 'selected' : ''}`}
                            onClick={() => handleCardSelect('new')}
                        >
                            Usar um novo cartão
                        </div>
                    </div>
                )}

                {selectedCard === 'new' && (
                    <CardElement />
                )}

                <button type="submit" disabled={!stripe || loading}>
                    {loading ? `Processando...` : `Pagar ${selectedPlan.price}`}
                </button>
            </form>

            {loading && (
                <div className="loading-section">
                    <div className="spinner"></div>
                    <p className="loading-text">Estamos verificando o seu pagamento ... só vai levar alguns segundos</p>
                </div>
            )}
        </div>
    );
};

export default CheckoutForm;

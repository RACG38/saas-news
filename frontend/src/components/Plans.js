import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';
import '../styles/Plans.css'; 
import CheckoutForm from './CheckoutForm';

// Initialize Stripe with your public key directly in the code
const stripePromise = loadStripe('pk_test_51Pn4lyFoYdflkG65WPti0iFUvKpCaTa4xSoGu9Zu2JvIAwbKhHfA73F9b2cO7DddKbrF6PXE05IXQ5o8DqFvQwE1007moBnRIJ');

const Plans = () => {
    const plans = [
        {
            plan_id: 1,
            plan_name: "Free",
            price: "R$0,00",
            features: ["Receba notícias diárias de até 5 ações¹", 
                       "Serão enviadas as 2 notícias mais relevantes sobre cada ativo por email"],
            color: "#b5efa1"
        },
        {
            plan_id: 2,
            plan_name: "Basic",
            price: "R$34,99",
            features: ["Receba notícias diárias de até 10 ações¹", 
                       "Serão enviadas as 5 notícias mais relevantes sobre cada ativo por email e whatsapp"],
            color: "#84b7ff"
        },
        {
            plan_id: 3,
            plan_name: "Pro",
            price: "R$49,99",
            features: ["Receba notícias diárias de até 30 ações¹",
                       "Serão enviadas as 5 notícias mais relevantes sobre cada ativo por email e whatsapp",
                       "Receba eventos em tempo real por whatsapp, como: pagamento de dividendos e mudança brusca do preço de cada ativo²"],
            color: "#fb8686"
        }
    ];

    const [isMenuOpen, setMenuOpen] = useState(false);
    const [selectedPlan, setSelectedPlan] = useState(null);
    const [showPopup, setShowPopup] = useState(false);
    const [paymentSuccess, setPaymentSuccess] = useState(null);
    const [paymentError, setPaymentError] = useState(null);  
    const [currentPlan, setCurrentPlan] = useState(null); 
    const [isPaymentInProgress, setIsPaymentInProgress] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();

    const { nome, email, whatsapp, password, change_plan } = location.state || {};

    useEffect(() => {
        const fetchCurrentPlan = async () => {
            try {
                
                const response = await fetch('http://localhost:8000/auth/plans/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: email,
                        action: 'get_current_plan',
                    }),
                });

                const data = await response.json();

                if (data.error) {
                    console.error('Erro ao buscar o plano atual:', data.error);
                } else {
                    setCurrentPlan(data);
                }
            } catch (error) {
                console.error('Erro ao buscar o plano atual:', error.message);
            }
        };

        fetchCurrentPlan();
    }, [email]);

    const handleFreeRegistration = async (plan) => {
        setIsLoading(true);  // Ativar o spinner
        try {
            const response = await fetch('http://localhost:8000/auth/plans/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    plan_id: plan.plan_id,
                    nome: nome,
                    email: email,
                    whatsapp: whatsapp,
                    password: password,
                    action: 'free_selected',
                    change_plan: change_plan
                }),
            });            
    
            const responseText = await response.text();            

            if (!response.ok) {
                throw new Error(responseText);
            }           
            
            setIsLoading(false);
            setShowPopup(true);
    
            setTimeout(() => {
                navigate('/login');
            }, 2000);
        } catch (error) {
            setIsLoading(false);
            console.error('Erro ao registrar o plano Free:', error.message);
        }
    };
    
    const handlePaymentResult = (result) => {
        if (result === 'success') {
            setPaymentSuccess(true);
            setPaymentError(false);
        } else {
            setPaymentSuccess(false);
            setPaymentError(true);
        }
    };

    const handlePaymentStart = () => {
        setIsPaymentInProgress(true); // Início do pagamento, desabilitar fechamento
    };

    const toggleMenu = (plan) => {
        
        if (plan.plan_id === currentPlan?.plan_id) {
            setShowPopup(true);
            setMenuOpen(false);  // Fechar o menu
            
        } else {
            if (plan.plan_id === 1) {
                // Feche o menu e não o reabra para Free
                setMenuOpen(false);
                handleFreeRegistration(plan);
            } else {
                
                setMenuOpen(true);  // Reabre o menu somente para planos pagos
                setShowPopup(false);  // Certifique-se de que o pop-up não seja exibido indevidamente
            }
        }

        setSelectedPlan(plan);
    };
    
    return (
        <div className="plans-container">            
            <h1>{change_plan ? 'Escolha um novo plano' : 'Escolha o plano que deseja adquirir'}</h1>
            <div className="plans">
                {plans.map((plan) => (
                    <div 
                        className="plan"
                        key={plan.plan_name} 
                        onClick={() => toggleMenu(plan)} 
                        style={{ cursor: 'pointer', backgroundColor: plan.color }} 
                    >
                        <h2>{plan.plan_name}</h2>
                        <p className="price">{plan.price}</p>
                        <ul>
                            {plan.features.map(feature => (
                                <li key={feature}>✓{feature}</li>
                            ))}
                        </ul>
                    </div>
                ))}
            </div>
            {selectedPlan && (
                <div className={`side-menu ${isMenuOpen ? 'open' : ''}`}>
                    <h2>Menu de Compra</h2>
                    <Elements stripe={stripePromise}>
                        <CheckoutForm
                            selectedPlan={selectedPlan}
                            userEmail={email}
                            userName={nome}
                            userWhatsapp={whatsapp}
                            userPassword={password}
                            navigate={navigate}
                            onPaymentResult={handlePaymentResult}
                            onPaymentStart={handlePaymentStart}
                            change_plan={change_plan}
                        />
                    </Elements>               
                    <button onClick={() => setMenuOpen(false)} disabled={isPaymentInProgress}>Fechar</button>
                    {paymentSuccess && (
                        <p style={{ color: 'green', fontSize: '18px', fontWeight: 'bold' }}>
                            ✅ Pagamento realizado com sucesso! Você será redirecionado para a tela de login
                        </p>
                    )}
                    {paymentError && (
                        <p style={{ color: 'red', fontSize: '18px', fontWeight: 'bold' }}>
                            ❌ O pagamento falhou. Verifique as informações do cartão e tente novamente.
                        </p>
                    )}
                </div>
            )}
            {showPopup && selectedPlan?.plan_id === currentPlan?.plan_id && (
                <div className="popup">
                    <p style={{ color: 'red', fontSize: '18px', fontWeight: 'bold' }}>
                        ❌ Você já possui este plano. Selecione um plano diferente.
                    </p>
                    <button onClick={() => setShowPopup(false)}>Fechar</button>
                </div>
            )}
            {showPopup && selectedPlan?.plan_id === 1 && selectedPlan?.plan_id !== currentPlan?.plan_id && (
                <div className="popup">
                    <p style={{ color: 'green', fontSize: '18px', fontWeight: 'bold' }}>
                        ✅ Cadastro realizado com sucesso! Você será redirecionado para o login.
                    </p>
                    <button onClick={() => setShowPopup(false)}>Fechar</button>
                </div>
            )}
            <div className="disclaimer">                
                <p>*Os preços e serviços podem ser alterados a qualquer momento sem aviso prévio. 
                Consulte os termos e condições para mais detalhes.</p>
                <p>(1) Todas as notícias são enviadas diariamente, todos os dias, após o fechamento do pregão da B3.</p>
                <p>(2) Eventos em tempo real serão enviados de segunda a sexta, exceto feriados, durante o pregão diário da B3.</p>
            </div>
            {isLoading && ( // Spinner aparece enquanto isLoading for true
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Carregando Plano Free</p>
                </div>
            )}
        </div>
    );
}

export default Plans;

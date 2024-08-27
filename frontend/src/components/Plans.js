import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '../styles/Plans.css'; 
import CheckoutForm from './CheckoutForm';

const Plans = () => {
    const plans = [
        {
            plan_id: 1,
            plan_name: "Freemium",
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
    const navigate = useNavigate();
    const location = useLocation();

    const { nome, email, whatsapp, password, change_plan } = location.state || {};

    const handleFreemiumRegistration = async (plan) => {
        
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
                    action: 'freemium_selected',
                    change_plan: change_plan
                }),
            });            
    
            const responseText = await response.text();            

            if (!response.ok) {
                throw new Error(responseText);
            }
    
            console.log('Cadastro Freemium realizado:', responseText);
            setShowPopup(true);
    
            setTimeout(() => {
                navigate('/login');
            }, 1000);
        } catch (error) {
            console.error('Erro ao registrar o plano Freemium:', error.message);
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

    const toggleMenu = (plan) => {
        
        if (plan.plan_name === "Freemium") {
            handleFreemiumRegistration(plan); 
        } else {   
            setSelectedPlan(plan);
            setMenuOpen(true); 
        }
    };

    return (
        <div className="plans-container">
            <h1>{change_plan ? 'Escolha um plano para upgrade' : 'Escolha o plano que deseja adquirir'}</h1>
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
                    <CheckoutForm
                        selectedPlan={selectedPlan}
                        userEmail={email}
                        userName={nome}
                        userWhatsapp={whatsapp}
                        userPassword={password}
                        navigate={navigate}
                        onPaymentResult={handlePaymentResult}
                        change_plan={change_plan}
                    />                  
                    <button onClick={() => setMenuOpen(false)}>Fechar</button>
                    {paymentSuccess && (
                        <p style={{ color: 'green', fontSize: '18px', fontWeight: 'bold' }}>
                            ✅ Pagamento realizado com sucesso!
                        </p>
                    )}
                    {paymentError && (
                        <p style={{ color: 'red', fontSize: '18px', fontWeight: 'bold' }}>
                            ❌ O pagamento falhou. Verifique as informações do cartão e tente novamente.
                        </p>
                    )}
                </div>
            )}
            {showPopup && (
                <div className="popup">
                    <p style={{ color: 'green', fontSize: '18px', fontWeight: 'bold' }}>
                        ✅ Cadastro realizado com sucesso! Você será redirecionado para o login.
                    </p>
                </div>
            )}
            <div className="disclaimer">                
                <p>*Os preços e serviços podem ser alterados a qualquer momento sem aviso prévio. 
                Consulte os termos e condições para mais detalhes.</p>
                <p>(1) Todas as notícias são enviadas diariamente, todos os dias, após o fechamento do pregão da B3.</p>
                <p>(2) Eventos em tempo real serão enviados de segunda a sexta, exceto feriados, durante o pregão diário da B3.</p>
            </div>
        </div>
    );
}

export default Plans;

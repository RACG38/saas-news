import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '../styles/Plans.css'; 
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';
import CheckoutForm from './CheckoutForm';

// Inicializa a chave pública do Stripe
const stripePromise = loadStripe('pk_test_51Pn4lyFoYdflkG65WPti0iFUvKpCaTa4xSoGu9Zu2JvIAwbKhHfA73F9b2cO7DddKbrF6PXE05IXQ5o8DqFvQwE1007moBnRIJ');

const Plans = () => {
    const plans = [
        {
            plan_id: 1,
            plan_name: "Freemium",
            price: "R$0,00",
            features: ["Receba notícias diárias de até 5 ações¹", 
                       "Serão enviadas as 2 notícias mais relevantes sobre cada ativo por email"],
            color: "green"
        },
        {
            plan_id: 2,
            plan_name: "Basic",
            price: "R$34,99",
            features: ["Receba notícias diárias de até 10 ações¹", 
                       "Serão enviadas as 5 notícias mais relevantes sobre cada ativo por email e whatsapp"],
            color: "blue"
        },
        {
            plan_id: 3,
            plan_name: "Pro",
            price: "R$49,99",
            features: ["Receba notícias diárias de até 30 ações¹",
                       "Serão enviadas as 5 notícias mais relevantes sobre cada ativo por email e whatsapp",
                       "Receba eventos em tempo real por whatsapp, como: pagamento de dividendos e mudança brusca do preço de cada ativo²"],
            color: "red"
        }
    ];

    const [isMenuOpen, setMenuOpen] = useState(false);
    const [selectedPlan, setSelectedPlan] = useState(null);
    const navigate = useNavigate();
    const location = useLocation();

    // Desestruturando os dados do usuário passados via navegação
    const { firstName, whatsapp, email, password } = location.state?.userData || {};

    const handleFreemiumRegistration = async (plan) => {
        try {
            const response = await fetch('http://localhost:8000/auth/plans/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    plano_id: plan.plan_id,
                    email: email,
                    username: firstName,
                    whatsapp: whatsapp,
                    password: password,
                    action: 'confirm_payment',  // Defina a ação conforme necessário
                }),
            });
    
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.message);
            }
    
            console.log('Cadastro Freemium realizado:', await response.json());
            navigate('/login');
        } catch (error) {
            console.error('Erro ao registrar o plano Freemium:', error.message);
        }
    };

    const toggleMenu = (plan) => {
        if (plan.plan_name === "Freemium") {
            handleFreemiumRegistration(plan); // Executa o registro diretamente para o plano Freemium
        } else {
            setSelectedPlan(plan);
            setMenuOpen(true); // Abre o menu de pagamento para outros planos
        }
    }

    return (
        <div className="plans-container">
            <h1>Escolha o plano que deseja adquirir</h1>
            <div className="plans">
                {plans.map((plan) => (
                    <div className="plan" key={plan.plan_name}>
                        <h2>{plan.plan_name}</h2>
                        <p className="price">{plan.price}</p>
                        <ul>
                            {plan.features.map(feature => (
                                <li key={feature}>✓{feature}</li>
                            ))}
                        </ul>
                        <button style={{ backgroundColor: plan.color }} onClick={() => toggleMenu(plan)}>Comprar</button>
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
                            userName={firstName}
                            userWhatsapp={whatsapp}
                            userPassword={password}
                            navigate={navigate}
                        />
                    </Elements>
                    <button onClick={() => setMenuOpen(false)}>Fechar</button>
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

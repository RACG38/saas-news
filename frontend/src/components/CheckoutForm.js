import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useStripe, useElements, CardNumberElement, CardExpiryElement, CardCvcElement } from '@stripe/react-stripe-js';
import '../styles/CheckoutForm.css';

const CheckoutForm = () => {
    const stripe = useStripe();
    const elements = useElements();
    const [loading, setLoading] = useState(false);
    const [cards, setCards] = useState([]);
    const [selectedCard, setSelectedCard] = useState('new');  // Default to 'new' for a new card
    const [cpf, setCpf] = useState('');
    const [cardholderName, setCardholderName] = useState('');
    const [billingAddress, setBillingAddress] = useState({
        cep: '',
        logradouro: '',
        numero: '',
        complemento: '',
        bairro: '',
        cidade: '',
        estado: '',
        pais: 'BR',
    });
    const [useBillingAsShipping, setUseBillingAsShipping] = useState(true);
    const [termsAccepted, setTermsAccepted] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();

    const { plano_id, email, whatsapp, name, password, change_plan } = location.state || {}; 

    useEffect(() => {
        // Fetch saved cards and address from the backend
        const fetchSavedData = async () => {
            try {
                const response = await fetch('http://localhost:8000/auth/checkout/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, action: 'get_card_info' }),
                });
                const data = await response.json();
                if (data.success) {
                    setCards(data.cards);  // Set the saved cards

                    // Se o endereço for retornado, preencha os campos
                    if (data.endereco) {
                        setBillingAddress(data.endereco);
                    }
                }
            } catch (error) {
                console.error('Erro ao buscar os cartões salvos e endereço:', error);
            }
        };

        fetchSavedData();
    }, [email]);

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
    
        if (!stripe || !elements) {
            setLoading(false);
            return;
        }
    
        let paymentMethod;
    
        if (selectedCard !== 'new') {
            // Se o cliente selecionou um cartão salvo, envie apenas o ID do cartão
            paymentMethod = { id: selectedCard };  // Envia apenas o ID do cartão salvo
        } else {
            // Cria um novo PaymentMethod para o novo cartão
            const cardNumberElement = elements.getElement(CardNumberElement);
            const { error: paymentMethodError, paymentMethod: newPaymentMethod } = await stripe.createPaymentMethod({
                type: 'card',
                card: cardNumberElement,
                billing_details: {
                    email: email,
                    name: cardholderName,
                },
            });
    
            if (paymentMethodError) {
                console.error('Erro ao criar PaymentMethod:', paymentMethodError.message);
                setLoading(false);
                return;
            }
    
            paymentMethod = newPaymentMethod;
        }
    
        try {
            const response = await fetch('http://localhost:8000/auth/checkout/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    plan_id: plano_id,
                    email: email,
                    cpf: cpf,
                    nome_titular: cardholderName,
                    billing_address: billingAddress,
                    payment_method: paymentMethod,  // Envia o PaymentMethod completo ou o ID do cartão salvo
                    change_plan_flag: change_plan,
                    address: {
                        logradouro: billingAddress.logradouro,
                        numero: billingAddress.numero,
                        complemento: billingAddress.complemento,
                        cidade: billingAddress.cidade,
                        bairro: billingAddress.bairro,
                        estado: billingAddress.estado,
                        cep: billingAddress.cep,
                        pais: billingAddress.pais,
                    },
                }),
            });
    
            const data = await response.json();
    
            if (response.status === 200 && data.success) {
                setTimeout(() => {
                    navigate('/login');
                }, 2000);
            } else {
                console.error('Erro ao criar a assinatura no backend:', data.error);
            }
        } catch (error) {
            console.error('Erro ao processar a assinatura:', error.message);
        } finally {
            setLoading(false);
        }
    };
    
    
    

    const handleCpfChange = (e) => {
        let value = e.target.value.replace(/\D/g, '');
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
        setCpf(value);
    };

    const handleCepChange = (e) => {
        let value = e.target.value.replace(/\D/g, '');  
        if (value.length > 5) {
            value = value.replace(/^(\d{5})(\d{1,3})/, '$1-$2');
        }
        setBillingAddress(prevState => ({
            ...prevState,
            cep: value,
        }));

        if (value.length === 9) {
            fetch(`https://viacep.com.br/ws/${value.replace('-', '')}/json/`)
                .then(response => response.json())
                .then(data => {
                    if (!data.erro) {
                        setBillingAddress(prevState => ({
                            ...prevState,
                            logradouro: data.logradouro,
                            bairro: data.bairro,
                            cidade: data.localidade,
                            estado: data.uf
                        }));
                    }
                })
                .catch(error => console.error('Erro ao buscar informações do CEP:', error));
        }
    };

    const handleBillingAddressChange = (e) => {
        const { name, value } = e.target;
        setBillingAddress(prevState => ({
            ...prevState,
            [name]: value,
        }));
    };

    const selectedPlan = {
        selectedPlan_id: parseInt(plano_id),
        plan_name: parseInt(plano_id) === 1 ? 'Free' : parseInt(plano_id) === 2 ? 'Basic' : 'Pro',
        price: parseInt(plano_id) === 1 ? 'R$ 0,00' : parseInt(plano_id) === 2 ? 'R$ 34,90' : 'R$ 49,90',
    };

    const today = new Date();
    const formattedDate = today.toLocaleDateString('pt-BR');

    return (
        <div className="checkout-container">
            <form className="payment-form" onSubmit={handleSubmit}>
                <h2>Forma de Pagamento</h2>
    
                {/* Dropdown para selecionar cartão salvo ou novo cartão */}
                {cards.length > 0 && (
                    <div className="form-group">
                        <label htmlFor="saved-card">Cartões Salvos</label>
                        <select
                            id="saved-card"
                            value={selectedCard}
                            onChange={(e) => setSelectedCard(e.target.value)}
                        >
                            <option value="new">Usar um novo cartão</option>
                            {cards.map((card) => (
                                <option key={card.id} value={card.id}>
                                    {card.brand.toUpperCase()} **** {card.last4} (Expira {card.exp_month}/{card.exp_year})
                                </option>
                            ))}
                        </select>
                    </div>
                )}
    
                {selectedCard === 'new' && (
                    <>
                        <div className="form-group">
                            <label>Número do cartão</label>
                            <CardNumberElement className="stripe-input" />
                        </div>
    
                        <div className="form-group inline-group">
                            <div className="inline-field">
                                <label>Validade (mês/ano)</label>
                                <CardExpiryElement className="stripe-input" />
                            </div>
                            <div className="inline-field">
                                <label>CVV</label>
                                <CardCvcElement className="stripe-input" />
                            </div>
                        </div>
                    </>
                )}
    
                {/* Informações de cobrança (CPF, Nome e Endereço) */}
                <div className="form-group">
                    <label htmlFor="cardholder-name">Nome do titular do cartão</label>
                    <input
                        type="text"
                        id="cardholder-name"
                        value={cardholderName}
                        placeholder="Nome do titular"
                        onChange={(e) => setCardholderName(e.target.value.toUpperCase())}
                    />
                </div>
    
                <div className="form-group">
                    <label htmlFor="cpf">CPF</label>
                    <input
                        type="text"
                        id="cpf"
                        value={cpf}
                        placeholder="CPF"
                        onChange={handleCpfChange}
                        maxLength="14"
                    />
                </div>
    
                {/* Endereço de cobrança */}
                <div className="billing-address">
                    <h3>Endereço de Cobrança</h3>
                    <div className="form-group inline-group">
                        <div className="inline-field">
                            <label>Código Postal (CEP)</label>
                            <input
                                type="text"
                                name="cep"
                                value={billingAddress.cep}
                                placeholder="00000-000"
                                onChange={handleCepChange}
                                maxLength="9"
                            />
                        </div>
                        <div className="inline-field">
                            <label>Logradouro</label>
                            <input
                                type="text"
                                name="logradouro"
                                value={billingAddress.logradouro}
                                onChange={handleBillingAddressChange}
                            />
                        </div>
                    </div>
    
                    <div className="form-group inline-group">
                        <div className="inline-field">
                            <label>Número</label>
                            <input
                                type="text"
                                name="numero"
                                value={billingAddress.numero}
                                onChange={handleBillingAddressChange}
                            />
                        </div>
                        <div className="inline-field">
                            <label>Complemento</label>
                            <input
                                type="text"
                                name="complemento"
                                value={billingAddress.complemento}
                                onChange={handleBillingAddressChange}
                            />
                        </div>
                    </div>
    
                    <div className="form-group inline-group">
                        <div className="inline-field">
                            <label>Bairro</label>
                            <input
                                type="text"
                                name="bairro"
                                value={billingAddress.bairro}
                                onChange={handleBillingAddressChange}
                            />
                        </div>
                        <div className="inline-field">
                            <label>Cidade</label>
                            <input
                                type="text"
                                name="cidade"
                                value={billingAddress.cidade}
                                onChange={handleBillingAddressChange}
                            />
                        </div>
                    </div>
    
                    <div className="form-group inline-group">
                        <div className="inline-field">
                            <label>Estado</label>
                            <input
                                type="text"
                                name="estado"
                                value={billingAddress.estado}
                                onChange={handleBillingAddressChange}
                            />
                        </div>
                        <div className="inline-field">
                            <label>País</label>
                            <input type="text" name="pais" value={billingAddress.pais} readOnly />
                        </div>
                    </div>
    
                    <div className="form-group checkbox-group">
                        <input
                            type="checkbox"
                            id="useBillingAsShipping"
                            checked={useBillingAsShipping}
                            onChange={() => setUseBillingAsShipping(!useBillingAsShipping)}
                        />
                        <label htmlFor="useBillingAsShipping">Usar como endereço de faturamento.</label>
                    </div>
                </div>
    
                <div className="form-group">
                    <input
                        type="checkbox"
                        id="termsAccepted"
                        checked={termsAccepted}
                        onChange={() => setTermsAccepted(!termsAccepted)}
                    />
                    <label htmlFor="termsAccepted">Eu estou ciente e de acordo com os <a href="/termos" target="_blank">Termos de uso</a></label>
                </div>
    
                <button type="submit" disabled={!stripe || loading || !termsAccepted}>
                    {loading ? 'Processando...' : `Pagar ${selectedPlan.price}`}
                </button>
            </form>
    
            <div className="plan-details">
                <h3>Plano {selectedPlan.plan_name}</h3>
                <p className="plan-price">{selectedPlan.price}/mês</p>
                <p>Cobrança mensal no dia {formattedDate}</p>
                <p className="plan-renewal">Renovação automática mensal</p>
            </div>
        </div>
    );
    
};

export default CheckoutForm;

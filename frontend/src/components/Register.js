/* eslint-disable no-unused-vars */

import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import '../styles/Register.css';

const Register = () => {
    const [firstName, setFirstName] = useState('');
    const [whatsapp, setWhatsapp] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState('');
    const [success, setSuccess] = useState(false);
    const [loading, setLoading] = useState(false); // Estado para gerenciar carregamento
    const [showSuccessMessage, setShowSuccessMessage] = useState(false); // Estado para exibir a mensagem de sucesso

    const location = useLocation();
    const navigate = useNavigate();
    const { plan_id, change_plan } = location.state || {};

    const formatPhoneNumber = (value) => {
        let phoneNumber = value.replace(/\D/g, '');
        if (phoneNumber.length > 11) {
            phoneNumber = phoneNumber.substring(0, 11);
        }
        if (phoneNumber.length > 10) {
            return phoneNumber.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
        } else if (phoneNumber.length > 5) {
            return phoneNumber.replace(/(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
        } else if (phoneNumber.length > 2) {
            return phoneNumber.replace(/(\d{2})(\d{0,5})/, '($1) $2');
        } else {
            return phoneNumber.replace(/(\d{0,2})/, '($1');
        }
    };

    const handleWhatsappChange = (e) => {
        const formattedNumber = formatPhoneNumber(e.target.value);
        setWhatsapp(formattedNumber);
    };

    const handleRegister = async (e) => {
        e.preventDefault();

        if (password !== confirmPassword) {
            setMessage('As senhas não coincidem');
            setSuccess(false);
            return;
        }

        const whatsappPattern = /^\(\d{2}\)\s\d{5}-\d{4}$/;
        if (!whatsappPattern.test(whatsapp)) {
            setMessage('Por favor, insira um número de WhatsApp válido');
            setSuccess(false);
            return;
        }

        setLoading(true); // Ativa o estado de carregamento ao iniciar a requisição

        try {
            const response = await fetch('http://localhost:8000/auth/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    nome: firstName,
                    email: email,
                    whatsapp: whatsapp.replace(/\D/g, ''),
                    password: password,
                    plan_id: plan_id,
                }),
            });

            const data = await response.json();

            if (data.success) {
                setSuccess(true);
                setShowSuccessMessage(true); // Exibe a mensagem de sucesso
                setMessage('Cadastro realizado com sucesso');
                setLoading(false);

                setTimeout(() => {
                    if (plan_id === 1) {
                        navigate('/login'); // Free Plan vai para login
                    } else {
                        navigate('/checkout', {
                            state: {
                                plan_id,
                                email,
                                whatsapp,
                                name: firstName,
                                password,
                                change_plan
                            }
                        });
                    }
                }, 2000); // Redireciona após 2 segundos
            } 
            else if (data.message === 'E-mail já cadastrado') {
                // Se o e-mail já estiver cadastrado, mostrar mensagem e redirecionar para login
                setMessage('E-mail já cadastrado. Por favor, faça o login.');
                setSuccess(false);
                setLoading(false);
                setTimeout(() => {
                    navigate('/login');
                }, 2000); // Redireciona para login após 2 segundos
            }            
            else {
                setMessage(data.message || 'Erro ao criar conta');
                setSuccess(false);
                setLoading(false); // Desativa o estado de carregamento
            }

        } catch (error) {
            console.error('Erro no registro:', error);
            setMessage('Erro interno do servidor');
            setSuccess(false);
            setLoading(false); // Desativa o estado de carregamento
        }
    };

    return (
        <div className="registration-container">
            <h2>Crie sua conta grátis</h2>
            <p>Faça o seu cadastro na plataforma para receber as principais notícias da sua carteira diariamente</p>
            <form onSubmit={handleRegister}>
                <input
                    type="text"
                    placeholder="Primeiro nome"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    required
                />
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
                <input
                    type="tel"
                    placeholder="Whatsapp"
                    value={whatsapp}
                    onChange={handleWhatsappChange}
                    required
                />
                <input
                    type="password"
                    placeholder="Senha"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Confirme a senha"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                />
                <button type="submit" disabled={loading}>
                    {loading ? 'Criando Conta...' : 'CRIAR CONTA'}
                </button>
                <p>Já possui cadastro? <Link to="/login">Faça o login</Link></p>
            </form>

            {loading && (
                <div className="loading-bar">
                    <div className="loading-bar-progress"></div>
                </div>
            )}

            {showSuccessMessage && (
                <div
                    className="success-message"
                    style={{
                        color: '#ff6f00',
                        border: '1px solid #ff6f00',
                        padding: '10px',
                        marginTop: '10px',
                        borderRadius: '5px',
                        textAlign: 'center',
                        fontWeight: 'bold',
                    }}
                >
                    Cadastro realizado com sucesso
                </div>
            )}

            {message && !showSuccessMessage && (
                <div
                    className={success ? 'message success' : 'message error'}
                    style={{
                        color: success ? 'green' : 'red',
                        border: `1px solid ${success ? 'green' : 'red'}`,
                        padding: '10px',
                        marginTop: '10px',
                        borderRadius: '5px',
                        textAlign: 'center',
                    }}
                >
                    {message}
                </div>
            )}
        </div>
    );
};

export default Register;

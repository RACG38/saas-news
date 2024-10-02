/* eslint-disable no-unused-vars */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import '../styles/Login.css';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const [isError, setIsError] = useState(false);
    const [loading, setLoading] = useState(false);
    const [typedText, setTypedText] = useState(''); // Estado para o efeito de digitação
    const [textIndex, setTextIndex] = useState(0); // Estado para controlar o índice da letra a ser exibida

    const navigate = useNavigate();
    const location = useLocation();

    const { selectedPlanName } = location.state || {};

    const fullText = "Fique por dentro de cada acontecimento das suas ações, em tempo real!";

    useEffect(() => {
        if (textIndex < fullText.length) {
            const timeout = setTimeout(() => {
                setTypedText(typedText + fullText[textIndex]);
                setTextIndex(textIndex + 1);
            }, 100); // Intervalo de 100ms para exibir cada letra

            return () => clearTimeout(timeout); // Limpar timeout a cada renderização
        }
    }, [textIndex, typedText, fullText]);

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            const response = await fetch('http://localhost:8000/auth/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    plano_nome: selectedPlanName
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Erro no login');
            }

            const data = await response.json();
            
            setMessage('Login bem-sucedido!');
            setIsError(false);

            localStorage.setItem('userId', data.cliente_id);

            setTimeout(() => {
                setLoading(false);
                navigate('/dashboard');
            }, 1000);

        } catch (error) {
            setMessage(error.message);
            setIsError(true);
            setLoading(false);
        }
    };

    const handleForgotPassword = () => {
        navigate('/forgotpassword');
    };

    return (
        <div className="login-page">
            {/* Parte esquerda com o texto animado */}
            <div className="login-left">
                <p className="animated-text">{typedText}</p>
            </div>

            {/* Parte direita com o formulário de login */}
            <div className="login-container">
                <h2>Olá! Seja Bem-vindo (a)!</h2>
                <p>Sincronize seus ativos na plataforma e acompanhe as principais notícias da sua carteira diariamente</p>
                <form className="login-form" onSubmit={handleLogin}>
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Senha"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <button type="submit" disabled={loading}>ENTRAR</button>
                    <a href="#" onClick={handleForgotPassword}>Esqueceu sua senha?</a>
                </form>
                {loading && (
                    <div className="loading-bar">
                        <div className="loading-bar-progress"></div>
                    </div>
                )}
                {message && (
                    <div
                        style={{
                            color: isError ? 'red' : 'orange',
                            border: `1px solid ${isError ? 'red' : 'orange'}`,
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
        </div>
    );
};

export default Login;

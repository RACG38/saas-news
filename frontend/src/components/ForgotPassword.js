/* eslint-disable no-unused-vars */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/ForgotPassword.css'; 

const ForgotPassword = () => {
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [isError, setIsError] = useState(false);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleForgotPassword = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await fetch('http://localhost:8000/auth/forgotpassword/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Erro ao solicitar recuperação de senha. Verifique o email digitado acima');
            }

            // const data = await response.json();
            setMessage('Instruções de redefinição de senha foram enviadas para o seu email.');
            setTimeout(() => {
                navigate('/verify-token');
            }, 2000);
            setIsError(false);
        } catch (error) {
            setMessage(error.message);
            setIsError(true);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="forgot-password-container">
            <h2>Recuperar Senha</h2>
            <p>Insira seu email para receber as instruções de recuperação de senha.</p>
            <form className="forgot-password-form" onSubmit={handleForgotPassword}>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
                <button type="submit" disabled={loading}>
                    {loading ? 'Enviando...' : 'Enviar Instruções'}
                </button>
            </form>
            {message && (
                <div
                    style={{
                        color: isError ? 'red' : 'green',
                        border: `1px solid ${isError ? 'red' : 'green'}`,
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

export default ForgotPassword;

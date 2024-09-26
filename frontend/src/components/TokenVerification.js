/* eslint-disable no-unused-vars */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Token.css';

const TokenVerification = () => {
    const [token, setToken] = useState(['', '', '', '', '', '']);
    const [message, setMessage] = useState('');
    const [isError, setIsError] = useState(false);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleInputChange = (e, index) => {
        const newToken = [...token];
        newToken[index] = e.target.value;
        setToken(newToken);

        // Move focus to the next input field
        if (e.target.value !== '' && index < 5) {
            document.getElementById(`token-${index + 1}`).focus();
        }
    };

    const handleTokenVerification = async (e) => {
        e.preventDefault();
        setLoading(true);
        const tokenString = token.join('');

        try {
            const response = await fetch(`http://localhost:8000/auth/verify-token/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    token: tokenString,                    
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Token inválido ou expirado');
            }

            // const data = await response.json();
            setMessage('Token verificado com sucesso. Redirecionando para redefinição de senha...');
            setIsError(false);

            setTimeout(() => {
                const tokenString = token.join(''); 
                navigate('/reset-password', { state: { token: tokenString } }); 
            }, 2000);

        } catch (error) {
            setMessage(error.message);
            setIsError(true);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="token-verification-container">
            <h2>Autorize seu login utilizando o Token ID recebido em seu email</h2>
            <p>Insira o código numérico de 6 dígitos abaixo</p>
            <form className="token-verification-form" onSubmit={handleTokenVerification}>
                <div className="token-inputs">
                    {token.map((digit, index) => (
                        <input
                            key={index}
                            id={`token-${index}`}
                            type="text"
                            maxLength="1"
                            value={digit}
                            onChange={(e) => handleInputChange(e, index)}
                            required
                        />
                    ))}
                </div>
                <p className="token-warning">
                    <i>Nunca pedimos seu Token por email, SMS, telefone, whatsapp ou qualquer outro canal. Não compartilhe esse código com ninguém.</i>
                </p>
                <button type="submit" disabled={loading}>
                    {loading ? 'Verificando...' : 'Confirmar e acessar conta'}
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

export default TokenVerification;

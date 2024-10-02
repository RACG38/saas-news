/* eslint-disable no-unused-vars */

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '../styles/ResetPassword.css';

const ResetPassword = () => {
    
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState('');
    const [isError, setIsError] = useState(false);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();
    
    // Obter o token do estado de navegação e garantir que seja uma string
    const token = location.state?.token || '';

    const handlePasswordReset = async (e) => {
        e.preventDefault();
        setLoading(true);

        if (password !== confirmPassword) {
            setMessage('As senhas não coincidem');
            setIsError(true);
            setLoading(false);
            return;
        }

        try {
            const response = await fetch(`http://localhost:8000/auth/reset-password/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    token: token,  // Enviar o token como string
                    password: password,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Erro ao redefinir a senha');
            }

            setMessage('Senha redefinida com sucesso. Redirecionando para login...');
            setIsError(false);

            setTimeout(() => {
                navigate('/login');
            }, 2000);

        } catch (error) {
            setMessage(error.message);
            setIsError(true);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="reset-password-container">
            <h2>Redefinir Senha</h2>
            <form className="reset-password-form" onSubmit={handlePasswordReset}>
                <input
                    type="password"
                    placeholder="Nova Senha"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Confirmar Nova Senha"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                />
                <button type="submit" disabled={loading}>
                    {loading ? 'Redefinindo...' : 'Redefinir Senha'}
                </button>
            </form>
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
    );
};

export default ResetPassword;

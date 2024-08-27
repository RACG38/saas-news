import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/ForgotPassword.css';

const TokenVerification = () => {
    
    const [token, setToken] = useState('');
    const [message, setMessage] = useState('');
    const [isError, setIsError] = useState(false);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleTokenVerification = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await fetch(`http://localhost:8000/auth/verify-token/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    token: token,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Token inválido ou expirado');
            }

            const data = await response.json();
            setMessage('Token verificado com sucesso. Redirecionando para redefinição de senha...');
            setIsError(false);

            setTimeout(() => {
                navigate(`/resetpassword/${token}`);
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
            <h2>Verificação de Token</h2>
            <p>Insira o token que você recebeu por email.</p>
            <form className="token-verification-form" onSubmit={handleTokenVerification}>
                <input
                    type="text"
                    placeholder="Token"
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                    required
                />
                <button type="submit" disabled={loading}>
                    {loading ? 'Verificando...' : 'Verificar Token'}
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

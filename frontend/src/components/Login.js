import React, { useState } from 'react';
import { Link, useNavigate, useLocation  } from 'react-router-dom';
import '../styles/Login.css';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const [isError, setIsError] = useState(false);
    const [loading, setLoading] = useState(false); // Estado para o carregamento
    const navigate = useNavigate();
    const location = useLocation();

    const { selectedPlanName } = location.state || {};

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true); // Ativa o carregamento
        
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

            // Simula um atraso para mostrar a barra de carregamento
            setTimeout(() => {
                setLoading(false); // Desativa o carregamento
                navigate('/dashboard');
            }, 1000); // 1 segundo de atraso (ajuste conforme necessário)

        } catch (error) {
            setMessage(error.message);
            setIsError(true);
            setLoading(false); // Desativa o carregamento em caso de erro
        }
    };

    const handleForgotPassword = () => {
        navigate('/forgotpassword');
    };

    return (
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
            <div className="social-login">
                {/* <button className="facebook-login">Continue com Facebook</button> */}
                {/* <button className="google-login">Continue com Google</button> */}
            </div>
            {/* <p>Não tem uma conta? <Link to="/register">Cadastre-se</Link></p> */}
            {loading && (
                <div className="loading-bar">
                    <div className="loading-bar-progress"></div>
                </div>
            )}
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

export default Login;

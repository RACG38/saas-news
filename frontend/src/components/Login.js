import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../styles/AuthStyles.css';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const [isError, setIsError] = useState(false);

    // Hook do React Router para navegar programaticamente
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch('http://localhost:8000/auth/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Erro no login');
            }

            const data = await response.json();
            console.log(data.message);
            setMessage('Login bem-sucedido!');
            setIsError(false);

            // Redirecionar para a página de painel após o login bem-sucedido
            navigate('/painel');

        } catch (error) {
            setMessage(error.message);
            setIsError(true);
        }
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
                <button type="submit">ENTRAR</button>
                <a href="#">Esqueceu sua senha?</a>
            </form>
            <div className="social-login">
                {/* <button className="facebook-login">Continue com Facebook</button> */}
                {/* <button className="google-login">Continue com Google</button> */}
            </div>
            <p>Não tem uma conta? <Link to="/register">Cadastre-se</Link></p>
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

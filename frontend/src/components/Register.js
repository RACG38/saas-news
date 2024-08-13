import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../styles/RegisterStyles.css';

const Register = () => {
    const [firstName, setFirstName] = useState('');
    const [whatsapp, setWhatsapp] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState('');
    const [success, setSuccess] = useState(false);

    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();

        if (password !== confirmPassword) {
            setMessage('As senhas não coincidem');
            setSuccess(false);
            return;
        }

        const whatsappPattern = /^[0-9]{10,15}$/;
        if (!whatsappPattern.test(whatsapp)) {
            setMessage('Por favor, insira um número de WhatsApp válido');
            setSuccess(false);
            return;
        }

        try {
            // Enviar dados para o backend para verificação ou pré-processamento, se necessário
            const response = await fetch('http://localhost:8000/auth/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: firstName,
                    email,
                    whatsapp,
                    password
                }),
            });

            const data = await response.json();

            if (data.redirect === 'plans') {
                // Redirecionar para a página de planos com os dados do usuário
                navigate('/plans', {
                    state: {
                        userData: {
                            firstName,
                            whatsapp,
                            email,
                            password
                        }
                    }
                });
            } else {
                setMessage(data.message);
                setSuccess(false);
            }

        } catch (error) {
            console.error('Erro no registro:', error);
            setMessage('Erro interno do servidor');
            setSuccess(false);
        }
    };

    return (
        <div className="registration-container">
            <h2>Crie sua conta grátis</h2>
            <p>Sincronize suas transações na plataforma e acompanhe a performance da sua carteira diariamente</p>
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
                    onChange={(e) => setWhatsapp(e.target.value)}
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
                <button type="submit">CRIAR CONTA</button>
                <div className="social-login-buttons">
                    {/* <button className="facebook">Continue com Facebook</button> */}
                    {/* <button className="google">Continue com Google</button> */}
                </div>
                <p>Já possui cadastro? <Link to="/">Faça o login</Link></p>
            </form>
            {message && (
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

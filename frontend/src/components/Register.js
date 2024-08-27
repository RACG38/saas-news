import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../styles/Register.css';

const Register = () => {
    const [firstName, setFirstName] = useState('');
    const [whatsapp, setWhatsapp] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState('');
    const [success, setSuccess] = useState(false);

    const navigate = useNavigate();

    const formatPhoneNumber = (value) => {
        // Remove tudo que não é número
        let phoneNumber = value.replace(/\D/g, '');

        // Limita o número de caracteres a 11 dígitos
        if (phoneNumber.length > 11) {
            phoneNumber = phoneNumber.substring(0, 11);
        }

        // Formata o número para (xx)xxxxx-xxxx
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

        // Atualização da expressão regular para corresponder ao formato correto
        const whatsappPattern = /^\(\d{2}\)\s\d{5}-\d{4}$/;
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
                    whatsapp: whatsapp.replace(/\D/g, ''), // Envia somente os números para o backend
                    password
                }),
            });

            const data = await response.json();

            if (data.redirect === 'plans') {

                navigate('/plans', { 
                    state: { 
                        nome: firstName, 
                        email: email, 
                        whatsapp: whatsapp, 
                        password: password, 
                        change_plan: false 
                    } 
                });
                
            } else if (data.redirect === 'login') {
                setMessage(data.message);
                setSuccess(true);
                // setTimeout(() => {
                //     navigate('/login', { state: { message: data.message } });
                // }, 3000);  // Delay de 3 segundos antes de redirecionar para o login
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
                    onChange={handleWhatsappChange}  // Use a função handleWhatsappChange
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

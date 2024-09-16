/* eslint-disable no-unused-vars */

import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import '../styles/Feedback.css';

const Feedback = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { nome: initialNome, email: initialEmail } = location.state || {}; // Pega os dados do estado ou define como undefined se não houver
    
    const [nome, setNome] = useState(initialNome || '');
    const [email, setEmail] = useState(initialEmail || '');
    const [feedback, setFeedback] = useState('');
    const [isFormValid, setIsFormValid] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false); // Estado para controlar se está enviando
    const [successMessage, setSuccessMessage] = useState(''); // Estado para controlar a mensagem de sucesso
    const [messageStyle, setMessageStyle] = useState({}); // Estado para controlar o estilo da mensagem

    // Função para validar se todos os campos estão preenchidos
    const validateForm = () => {
        if (nome.trim() !== '' && email.trim() !== '' && feedback.trim() !== '') {
            setIsFormValid(true);
        } else {
            setIsFormValid(false);
        }
    };

    useEffect(() => {
        validateForm(); // Valida o formulário sempre que o nome, email ou feedback mudar
    }, [nome, email, feedback]);

    // Atualiza os campos e valida o formulário
    const handleNomeChange = (e) => {
        setNome(e.target.value);
        validateForm();
    };

    const handleEmailChange = (e) => {
        setEmail(e.target.value);
        validateForm();
    };

    const handleFeedbackChange = (e) => {
        setFeedback(e.target.value);
        validateForm();
    };

    // Função para enviar o email com os dados preenchidos
    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!isFormValid) {
            alert("Por favor, preencha todos os campos.");
            return;
        }

        setIsSubmitting(true); // Inicia o estado de envio

        // Configurar os dados para envio do feedback
        const feedbackData = {
            nome,
            email,
            mensagem: feedback
        };

        try {
            const response = await fetch('http://localhost:8000/auth/feedback/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(feedbackData),
            });

            if (response.ok) {
                setSuccessMessage('Feedback enviado com sucesso!'); // Mensagem de sucesso
                setMessageStyle({
                    color: 'green', // Cor customizada
                    fontSize: '18px', // Tamanho customizado
                    fontWeight: 'bold', // Estilo customizado
                    textAlign: 'center',
                    margin: '20px 0'                    
                });
                setTimeout(() => {
                    navigate('/login');  // Redireciona para a página de login após 3 segundos
                }, 3000);
            } else {
                alert('Erro ao enviar feedback. Por favor, tente novamente.');
            }
        } catch (error) {
            console.error('Erro ao enviar o feedback:', error);
            alert('Erro ao enviar feedback. Por favor, tente novamente.');
        } finally {
            setIsSubmitting(false); // Finaliza o estado de envio
        }
    };

    return (
        <div className="feedback-form-container">
            <h2>Feedback e Sugestões</h2>
            {successMessage ? (
                <p style={messageStyle}>{successMessage}</p> // Exibe a mensagem de sucesso com estilo customizado
            ) : (
                <form onSubmit={handleSubmit} className="feedback-form">
                    <label>
                        Nome:
                        <input
                            type="text"
                            value={nome}
                            onChange={handleNomeChange}
                            required
                            disabled={initialNome}  // Desabilitar o campo se o nome vier do estado
                        />
                    </label>
                    <label>
                        Email:
                        <input
                            type="email"
                            value={email}
                            onChange={handleEmailChange}
                            required
                            disabled={initialEmail}  // Desabilitar o campo se o email vier do estado
                        />
                    </label>
                    <label>
                        Feedback e Sugestões:
                        <textarea
                            value={feedback}
                            onChange={handleFeedbackChange}
                            rows="5"
                            required
                        />
                    </label>
                    <button type="submit" disabled={!isFormValid || isSubmitting}>
                        {isSubmitting ? 'Enviando...' : 'Enviar'}
                    </button>
                    {isSubmitting && <div className="spinner"></div>} {/* Mostra o spinner */}
                </form>
            )}
        </div>
    );
};

export default Feedback;

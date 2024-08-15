import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Dashboard.css';

const Dashboard = () => {
    const [userData, setUserData] = useState(null);  // Inicialize com null
    const [selectedStocks, setSelectedStocks] = useState([]);
    const [filterLetter, setFilterLetter] = useState(''); // Estado para armazenar a letra filtrada
    const navigate = useNavigate();

    useEffect(() => {
        const userId = localStorage.getItem('userId');
        fetch(`http://localhost:8000/auth/dashboard/?cliente_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            console.log("Dados recebidos da API:", data);
            if (data) {
                const uniqueStocks = removeDuplicates(data.acoes_disponiveis);
                setUserData({ ...data, acoes_disponiveis: uniqueStocks });
                setSelectedStocks(data.acoes_selecionadas ? data.acoes_selecionadas.map(acao => acao.simbolo) : []);
            } else {
                setUserData({ error: "Dados do usuário não encontrados" });
            }
        })
        .catch(error => {
            console.error('Erro ao buscar dados do usuário:', error);
            setUserData({ error: "Erro ao buscar dados do usuário" });
        });
    }, [navigate]);

    const removeDuplicates = (stocks) => {
        const seen = new Set();
        return stocks.filter(stock => {
            const duplicate = seen.has(stock.simbolo);
            seen.add(stock.simbolo);
            return !duplicate;
        });
    };

    const handleStockSelection = (simbolo) => {
        if (selectedStocks.includes(simbolo)) {
            setSelectedStocks(prevSelectedStocks => prevSelectedStocks.filter(stock => stock !== simbolo));
        } else {
            setSelectedStocks(prevSelectedStocks => [...prevSelectedStocks, simbolo]);
        }
    };

    const handleSave = () => {
        fetch(`http://localhost:8000/auth/dashboard/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userId: localStorage.getItem('userId'),
                selectedStocks,
            }),
        })
        .then(response => response.json())
        .then(data => {
            alert('Ações salvas com sucesso!');
            fetchData(); // Atualizar a lista de ações selecionadas
        })
        .catch(error => {
            console.error('Erro ao salvar ações:', error);
        });
    };

    const fetchData = () => {
        fetch(`http://localhost:8000/auth/dashboard/`)
        .then(response => response.json())
        .then(data => {
            if (data) {
                const uniqueStocks = removeDuplicates(data.acoes_disponiveis);
                setUserData({ ...data, acoes_disponiveis: uniqueStocks });
                setSelectedStocks(data.acoes_selecionadas ? data.acoes_selecionadas.map(acao => acao.simbolo) : []);
            }
        })
        .catch(error => {
            console.error('Erro ao buscar dados do usuário:', error);
        });
    };

    const handleLogout = () => {
        localStorage.removeItem('userId');
        navigate('/login');
    };

    const calculateNextBillingDate = (lastPaymentDate) => {
        if (!lastPaymentDate) return 'N/A';
        const date = new Date(lastPaymentDate);
        date.setDate(date.getDate() + 30);
        return date.toLocaleDateString();
    };

    const handleLetterFilter = (letter) => {
        setFilterLetter(letter.toUpperCase());
    };

    const handleClearSelection = () => {
        setSelectedStocks([]);
    };

    const getAvailableLetters = () => {
        const letters = new Set();
        userData?.acoes_disponiveis?.forEach(acao => {
            const firstLetter = acao.simbolo.trim().toUpperCase().charAt(0);
            letters.add(firstLetter);
        });
        return Array.from(letters).sort();
    };

    const availableLetters = getAvailableLetters();

    const filteredStocks = userData?.acoes_disponiveis?.filter(acao => {
        const simbolo = acao.simbolo.trim().toUpperCase(); // Remove espaços em branco ao redor
        return simbolo.startsWith(filterLetter);
    }) || [];

    if (!userData) return <div>Carregando...</div>;  // Verifique se userData está definido

    return (
        <div className="dashboard">
            <div className="sidebar">
                <h3>Painel de configurações da conta</h3>
                <p><strong>Nome:</strong> {userData.cliente ? userData.cliente.nome : 'N/A'}</p>
                <p><strong>Plano atual:</strong> {userData.cliente && userData.cliente.plano ? userData.cliente.plano.nome_plano : 'N/A'}</p>
                <p><strong>Quantidade de Ativos:</strong> {userData.cliente && userData.cliente.plano ? userData.cliente.plano.qtdade_ativos : 'N/A'}</p>
                <p><strong>Quantidade de Notícias:</strong> {userData.cliente && userData.cliente.plano ? userData.cliente.plano.qtdade_noticias : 'N/A'}</p>
                <p><strong>Email:</strong> {userData.cliente && userData.cliente.plano ? (userData.cliente.plano.email_opt ? 'Sim' : 'Não') : 'N/A'}</p>
                <p><strong>WhatsApp:</strong> {userData.cliente && userData.cliente.plano ? (userData.cliente.plano.whatsapp_opt ? 'Sim' : 'Não') : 'N/A'}</p>
                <p><strong>Tempo Real:</strong> {userData.cliente && userData.cliente.plano ? (userData.cliente.plano.temporeal ? 'Sim' : 'Não') : 'N/A'}</p>
                                
                <button onClick={handleClearSelection} className="sidebar-button clear-selection">Limpar Seleção</button>

                <div style={{ flexGrow: 1 }}></div> {/* Espaço flexível para empurrar o botão "Salvar" para baixo */}
                
                <button onClick={handleSave} className="sidebar-button">Salvar</button>
                <button onClick={handleLogout} className="sidebar-button">Logout</button>
            </div>
            <div className="content">                
                <div className="stocks-section">
                    <div className="letter-filter">
                        {availableLetters.map(letter => (
                            <span 
                                key={letter} 
                                className={`filter-letter ${filterLetter === letter ? 'active' : ''}`} 
                                onClick={() => handleLetterFilter(letter)}
                            >
                                {letter}
                            </span>
                        ))}
                    </div>
                    <h4>Escolha as ações:</h4>
                    <div className="stocks-grid">
                        {filteredStocks.length > 0 ? (
                            filteredStocks.map((acao) => (
                                <div 
                                    key={acao.simbolo} 
                                    className={`stock-card ${selectedStocks.includes(acao.simbolo) ? 'selected' : ''}`}
                                    onClick={() => handleStockSelection(acao.simbolo)}
                                >
                                    <p>{acao.simbolo}</p>
                                    <p>{acao.nome}</p>
                                </div>
                            ))
                        ) : <p>Nenhuma ação disponível.</p>}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;

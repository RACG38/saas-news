import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSignOutAlt } from '@fortawesome/free-solid-svg-icons';
import '../styles/Dashboard.css';

const Dashboard = () => {
    const [userData, setUserData] = useState(null);
    const [selectedStocks, setSelectedStocks] = useState([]);
    const [filterLetter, setFilterLetter] = useState('');
    const [error, setError] = useState(''); 
    const [initialLoad, setInitialLoad] = useState(true);
    const [showMyStocks, setShowMyStocks] = useState(false); 
    const navigate = useNavigate();

    useEffect(() => {
        fetchData(); 
    }, [navigate]);

    const removeDuplicates = (stocks) => {
        const seen = new Set();
        return stocks.filter(stock => {
            const duplicate = seen.has(stock.simbolo);
            seen.add(stock.simbolo);
            return !duplicate;
        });
    };

    const fetchData = () => {
        const userId = localStorage.getItem('userId');
        fetch(`http://localhost:8000/auth/dashboard/?cliente_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            
            if (data) {
                const uniqueStocks = removeDuplicates(data.acoes_disponiveis);
                setUserData({ ...data, acoes_disponiveis: uniqueStocks });

                if (data.acoes_selecionadas && data.acoes_selecionadas.length > 0) {
                    setSelectedStocks(data.acoes_selecionadas.map(acao => acao.simbolo));
                    setFilterLetter(''); 
                } else {
                    setFilterLetter(''); 
                }

                setInitialLoad(false);
            } else {
                setUserData({ error: "Dados do usuário não encontrados" });
            }
        })
        .catch(error => {
            console.error('Erro ao buscar dados do usuário:', error);
            setUserData({ error: "Erro ao buscar dados do usuário" });
        });
    };

    const handleStockSelection = (simbolo) => {
        const maxAtivos = userData?.cliente?.plano?.qtdade_ativos || 0;
        const isSelected = selectedStocks.includes(simbolo);

        if (isSelected) {
            setSelectedStocks(prevSelectedStocks => prevSelectedStocks.filter(stock => stock !== simbolo));
        } else {
            if (selectedStocks.length < maxAtivos) {
                setSelectedStocks(prevSelectedStocks => [...prevSelectedStocks, simbolo]);
                setError(''); 
            } else {
                setError(`Você só pode selecionar até ${maxAtivos} ativos.`);
            }
        }
    };

    const handleSave = () => {
        const selectedStocksData = selectedStocks.map(simbolo => {
            const stock = userData.acoes_disponiveis.find(acao => acao.simbolo === simbolo);
            return { simbolo: stock.simbolo, nome: stock.nome };
        });

        fetch(`http://localhost:8000/auth/dashboard/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userId: localStorage.getItem('userId'),
                selectedStocks: selectedStocksData,
            }),
        })
        .then(response => response.json())
        .then(data => {
            alert('Ações salvas com sucesso!');
            fetchData(); 
        })
        .catch(error => {
            console.error('Erro ao salvar ações:', error);
        });
    };

    const handleLogout = () => {
        localStorage.removeItem('userId');
        navigate('/login');
    };

    const handleLetterFilter = (letter) => {
        setFilterLetter(letter.toUpperCase());
        setShowMyStocks(false); 
    };

    const handleClearSelection = () => {
        setSelectedStocks([]);
        setError(''); 
    };

    const handleShowMyStocks = () => {
        setFilterLetter(''); 
        setShowMyStocks(true); 
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
        const simbolo = acao.simbolo.trim().toUpperCase();

        if (showMyStocks) {
            return selectedStocks.includes(simbolo);
        } else if (filterLetter) {
            return simbolo.startsWith(filterLetter);
        } else if (initialLoad) {
            return selectedStocks.includes(simbolo) || selectedStocks.length === 0;
        } else {
            return true;
        }
    }) || [];

    if (!userData) return <div>Carregando...</div>;

    return (
        <div className="dashboard">
            <div className="sidebar">
                <p><strong>Olá </strong> {userData.cliente ? userData.cliente.nome : 'N/A'}</p>
                <p><strong>Plano </strong> {userData.cliente && userData.cliente.plano ? userData.cliente.plano.nome : 'N/A'}</p>
                <h3 className="custom-heading">Painel de configurações da conta</h3>             
                
                <p><strong>Quantidade de Ativos:</strong> {userData.cliente && userData.cliente.plano ? userData.cliente.plano.qtdade_ativos : 'N/A'}</p>
                <p><strong>Quantidade de Notícias:</strong> {userData.cliente && userData.cliente.plano ? userData.cliente.plano.qtdade_noticias : 'N/A'}</p>
                <p><strong>Email:</strong> {userData.cliente && userData.cliente.plano ? (userData.cliente.plano.email_opt ? 'Sim' : 'Não') : 'N/A'}</p>
                <p><strong>WhatsApp:</strong> {userData.cliente && userData.cliente.plano ? (userData.cliente.plano.whatsapp_opt ? 'Sim' : 'Não') : 'N/A'}</p>
                <p><strong>Tempo Real:</strong> {userData.cliente && userData.cliente.plano ? (userData.cliente.plano.temporeal ? 'Sim' : 'Não') : 'N/A'}</p>

                {error && <p className="error-message">{error}</p>} 
                
                <button onClick={handleClearSelection} className="sidebar-button clear-selection">Limpar Seleção</button>

                <div style={{ flexGrow: 1 }}></div>
                
                <button onClick={handleSave} className="sidebar-button save">Salvar</button>
                
                <div className="logout-container" onClick={handleLogout}>
                    <FontAwesomeIcon icon={faSignOutAlt} size="2x" className="logout-icon" />
                    <span className="logout-text">LOG OUT</span>
                </div>
            </div>
            <div className="content">                
                <div className="stocks-section">
                    <div className="letter-filter">
                        <span 
                            className={`filter-letter ${showMyStocks ? 'active' : ''}`} 
                            onClick={handleShowMyStocks}
                        >
                            Minhas Ações
                        </span>
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
                    {showMyStocks && filteredStocks.length === 0 ? (
                        <div style={{ textAlign: 'center', color: 'white', marginTop: '300px', fontSize: 30}}>
                            <h2>📈 Você ainda não possui ações selecionadas.</h2>
                            <h2>Navegue pelos índices acima para escolher suas ações 📈</h2>
                        </div>
                    ) : (
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
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;

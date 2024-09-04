import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSignOutAlt } from '@fortawesome/free-solid-svg-icons';
import '../styles/Dashboard.css';

const getStockImagePath = async (symbol) => {
    const prefix = symbol.slice(0, 4);
    const svgImagePath = `/images/${prefix}.svg`;
    const jpgImagePath = `/images/${prefix}.jpg`;

    try {
        let response = await fetch(svgImagePath);
        if (response.status === 200 && response.headers.get('content-type').includes('image/svg+xml')) {
            return svgImagePath;
        } 
        
        response = await fetch(jpgImagePath);
        if (response.status === 200 && response.headers.get('content-type').includes('image/jpeg')) {
            return jpgImagePath;
        }

        return '/images/default.svg';

    } catch (error) {
        console.error(`Erro ao buscar a imagem para: ${prefix}`, error);
        return '/images/default.svg';
    }
};

const Dashboard = () => {
    const [userData, setUserData] = useState(null);
    const [selectedStocks, setSelectedStocks] = useState([]);
    const [filterLetter, setFilterLetter] = useState('');
    const [error, setError] = useState(''); 
    const [showMyStocks, setShowMyStocks] = useState(false); 
    const [stocksWithImages, setStocksWithImages] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showSuccessModal, setShowSuccessModal] = useState(false);
    const [showLimitModal, setShowLimitModal] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        fetchImages();
    }, [navigate]);

    const fetchImages = async () => {
        const userId = localStorage.getItem('userId');
        const response = await fetch(`http://localhost:8000/auth/dashboard/?cliente_id=${userId}`);
        const data = await response.json();

        if (data) {
            const uniqueStocks = removeDuplicates(data.acoes_disponiveis);
            setUserData({ ...data, acoes_disponiveis: uniqueStocks });

            const updatedStocks = await Promise.all(uniqueStocks.map(async (acao) => {
                const imagePath = await getStockImagePath(acao.simbolo);
                return { ...acao, imagePath };
            }));
            setStocksWithImages(updatedStocks);

            if (data.acoes_selecionadas && data.acoes_selecionadas.length > 0) {
                setSelectedStocks(data.acoes_selecionadas.map(acao => acao.simbolo));
                setShowMyStocks(true); 
            }

            setLoading(false);
        }
    };

    const removeDuplicates = (stocks) => {
        const seen = new Set();
        return stocks.filter(stock => {
            const duplicate = seen.has(stock.simbolo);
            seen.add(stock.simbolo);
            return !duplicate;
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
                setShowLimitModal(true);
            }
        }
    };

    const handleSave = () => {
        console.log("handleSave foi chamado");
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
            console.log("Resposta do servidor:", data);
            setShowSuccessModal(true);
            setShowMyStocks(true); 
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

    const handleChangePlanClick = () => {
        
        // const { firstName, email, whatsapp, password } = userData;
        
        navigate('/plans', { 
            state: { 
                nome: userData.cliente.nome, 
                email: userData.cliente.email, 
                whatsapp: userData.cliente.whatsapp, 
                password: userData.cliente.password, 
                change_plan: true 
            } 
        });
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

    const filteredStocks = stocksWithImages
    .filter(acao => {
        const simbolo = acao.simbolo.trim().toUpperCase();

        if (showMyStocks) {
            return selectedStocks.includes(simbolo);
        } else if (filterLetter) {
            return simbolo.startsWith(filterLetter);
        } else {
            return true;
        }
    })
    .sort((a, b) => a.simbolo.localeCompare(b.simbolo));

    if (loading) {
        return (
            <div className="spinner-container">
                <div className="spinner"></div>
            </div>
        );
    }

    return (
        <div className="dashboard">
            <div className="sidebar">
                <h3 className="custom-heading">Painel de configurações da conta</h3>
                <p><strong>Olá </strong> {userData.cliente ? userData.cliente.nome : 'N/A'}</p>
                <p><strong>Plano </strong> {userData.cliente && userData.cliente.plano ? userData.cliente.plano.nome : 'N/A'}</p>               
                <p><strong>Quantidade de Ativos:</strong> {userData.cliente && userData.cliente.plano ? userData.cliente.plano.qtdade_ativos : 'N/A'}</p>
                <p><strong>Quantidade de Notícias:</strong> {userData.cliente && userData.cliente.plano ? userData.cliente.plano.qtdade_noticias : 'N/A'}</p>
                <p><strong>Email:</strong> {userData.cliente && userData.cliente.plano ? (userData.cliente.plano.email_opt ? 'Sim' : 'Não') : 'N/A'}</p>
                <p><strong>WhatsApp:</strong> {userData.cliente && userData.cliente.plano ? (userData.cliente.plano.whatsapp_opt ? 'Sim' : 'Não') : 'N/A'}</p>
                <p><strong>Tempo Real:</strong> {userData.cliente && userData.cliente.plano ? (userData.cliente.plano.temporeal ? 'Sim' : 'Não') : 'N/A'}</p>

                {error && <p className="error-message">{error}</p>} 

                <div style={{ flexGrow: 1 }}></div>

                <button onClick={handleSave} className="sidebar-button save">Salvar Seleção</button>
                
                <button onClick={handleClearSelection} className="sidebar-button clear-selection">Limpar Seleção</button>

                <p onClick={handleChangePlanClick} className="upgrade-plan-link">
                    Quero mudar o meu plano
                </p>
                            
                <div className="logout-container" onClick={handleLogout}>
                    <FontAwesomeIcon icon={faSignOutAlt} size="2x" className="logout-icon" />
                    <span className="logout-text">LOG OUT</span>
                </div>
            </div>
            <div className="content">                
                <div className="stocks-section">
                <div className="letter-filter-container">
                        <div className="letter-filter">
                            <span 
                                className={`filter-letter ${showMyStocks ? 'active' : ''}`} 
                                onClick={handleShowMyStocks}
                            >
                                Minhas Ações
                            </span>
                            <span 
                                className={`filter-letter ${!showMyStocks && filterLetter === '' ? 'active' : ''}`} 
                                onClick={() => { 
                                    setShowMyStocks(false); 
                                    setFilterLetter(''); 
                                }}
                            >
                                Mostrar Todas
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
                    </div>


                    <p style={{ textAlign: 'left', color: '#ffffff', margin: '70px 0 70px 20px', fontSize: '22px' }}>
                        Quantidade de empresas exibidas: {filteredStocks.length}
                    </p>

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
                                        <div className="image-container">
                                            <img 
                                                src={acao.imagePath} 
                                                alt={`${acao.nome} logo`} 
                                                className="stock-image"
                                            />
                                        </div>
                                        <div className="symbol-container">
                                            <p className="stock-symbol">{acao.simbolo}</p>
                                        </div>
                                    </div>
                                ))
                            ) : <p>Nenhuma ação disponível.</p>}
                        </div>
                    )}
                </div>
            </div>

            {showSuccessModal && (
                <div className="modal">
                    <div className="modal-content">
                        <h2>✅ Ações salvas com sucesso!</h2>
                        <button onClick={() => setShowSuccessModal(false)}>Fechar</button>
                    </div>
                </div>
            )}
            {showLimitModal && (
                <div className="modal">
                    <div className="modal-content">
                        <h2>⚠️ Limite de Ações Atingido</h2>
                        <p>Você atingiu o limite de {userData?.cliente?.plano?.qtdade_ativos} ações para o plano {userData?.cliente?.plano?.nome}.
                            Exclua alguma ação na seção "Minhas Ações" para poder selecionar outra.
                        </p>
                        <button onClick={() => setShowLimitModal(false)}>Fechar</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;

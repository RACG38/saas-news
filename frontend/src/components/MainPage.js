import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '../styles/MainPage.css';

const MainPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { plano_id, nome, email, change_plan } = location.state || {};  // Usar plan_nome para saber o plano atual do cliente
  
  // Lógica para redirecionar para checkout ou registro
  const handleCheckoutClick = (selectedPlanName) => {

    if (change_plan && selectedPlanName === 'Free' && plano_id !== 1) {      
      // Se o cliente está mudando de plano, não está no plano Free e tenta selecionar o Free, redireciona para o login
      navigate('/login', { state: { selectedPlanName } });
    } else {
      // Caso contrário, segue o fluxo normal para o checkout ou registro
      if (change_plan) {        
        navigate('/checkout', { state: { plano_id: selectedPlanName === 'Free' ? 1 : selectedPlanName === 'Basic' ? 2 : 3, email, nome, change_plan } });
      } else {
        navigate('/register', { state: { plano_id: selectedPlanName === 'Free' ? 1 : selectedPlanName === 'Basic' ? 2 : 3, change_plan } });
      }
    }
  };

  const handleLoginClick = () => {
    navigate('/login'); // Redireciona para a página de login
  };

  const isCurrentPlan = (plan) => plano_id === plan; // Verifica se é o plano atual do cliente

  return (
    <div>
      {/* Cabeçalho com opção de Login */}
      <header>
        <div className="header-container">
          <h1>News APP</h1>
          <nav>
            <ul>
              <li><a href="#" onClick={handleLoginClick}>Login</a></li>
            </ul>
          </nav>
        </div>
      </header>

      {/* Seção de Boas-vindas */}
      <section className="intro-section">
        <div className="container">
          <h2>Bem-vindo ao Nosso Serviço</h2>
          <p>Escolha o plano que melhor se adapta às suas necessidades</p>
        </div>
      </section>

      {/* Seção de Planos de Preço */}
      <section className="pricing-section">
        <div className="container">
          <h2>Nossos Planos</h2>
          <table className="pricing-table">
            <thead>
              <tr>
                <th>Funcionalidades</th>
                <th>Free</th>
                <th>Basic</th>
                <th>Pro</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Recebimento de notícias diariamente</td>
                <td><span className="check-icon">&#10003;</span></td>
                <td><span className="check-icon">&#10003;</span></td>
                <td><span className="check-icon">&#10003;</span></td>
              </tr>
              <tr>
                <td>Notícias enviadas por e-mail</td>
                <td><span className="check-icon">&#10003;</span></td>
                <td><span className="check-icon">&#10003;</span></td>
                <td><span className="check-icon">&#10003;</span></td>
              </tr>
              <tr>
                <td>Notícias enviadas por whatsapp</td>
                <td>---</td>
                <td><span className="check-icon">&#10003;</span></td>
                <td><span className="check-icon">&#10003;</span></td>
              </tr>
              <tr>
                <td>Aviso de pagamento de dividendos por e-mail</td>
                <td>---</td>
                <td><span className="check-icon">&#10003;</span></td>
                <td><span className="check-icon">&#10003;</span></td>
              </tr>
              <tr>
                <td>Recebimento de notícias das suas ações em tempo real</td>
                <td>---</td>
                <td>---</td>
                <td><span className="check-icon">&#10003;</span></td>
              </tr>
              <tr>
                <td>Análise de sentimento das suas ações</td>
                <td>---</td>
                <td>---</td>
                <td><span className="check-icon">&#10003;</span></td>
              </tr>
              <tr>
                <td>Quantidade de ações para cadastrar</td>
                <td>5</td>
                <td>10</td>
                <td>25</td>
              </tr>
              <tr>
                <td>Quantidade de notícias recebidas</td>
                <td>2</td>
                <td>3</td>
                <td>5</td>
              </tr>
              <tr>
                <td></td>
                <td>
                  <button 
                    className={`btn btn-free ${isCurrentPlan(1) ? 'current-plan' : ''}`} 
                    onClick={() => handleCheckoutClick('Free')} 
                    disabled={isCurrentPlan(1)}  // Desabilita o botão se o plano atual for 'Free'
                  >
                    Escolher Free
                  </button>
                </td>
                <td>
                  <button 
                    className={`btn btn-basic ${isCurrentPlan(2) ? 'current-plan' : ''}`} 
                    onClick={() => handleCheckoutClick('Basic')} 
                    disabled={isCurrentPlan(2)}  // Desabilita o botão se o plano atual for 'Basic'
                  >
                    Escolher Basic
                  </button>
                </td>
                <td>
                  <button 
                    className={`btn btn-pro ${isCurrentPlan(3) ? 'current-plan' : ''}`} 
                    onClick={() => handleCheckoutClick('Pro')} 
                    disabled={isCurrentPlan(3)}  // Desabilita o botão se o plano atual for 'Pro'
                  >
                    Escolher Pro
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          {/* Texto indicando "Seu plano atual" abaixo da tabela */}
          <div className="current-plan-container">
            {isCurrentPlan('Free') && <span className="current-plan-label current-plan-free">Seu plano atual</span>}
            {isCurrentPlan('Basic') && <span className="current-plan-label current-plan-basic">Seu plano atual</span>}
            {isCurrentPlan('Pro') && <span className="current-plan-label current-plan-pro">Seu plano atual</span>}
          </div>

        </div>
      </section>

      {/* Rodapé */}
      <footer>
        <div className="container">
          <p>&copy; 2024 Seu Serviço. Todos os direitos reservados.</p>
        </div>
      </footer>
    </div>
  );
};

export default MainPage;

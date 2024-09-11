import React, { useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheckCircle, faTimesCircle } from '@fortawesome/free-solid-svg-icons';
import '../styles/MainPage.css'; // Certifique-se de que o arquivo CSS está corretamente importado

const MainPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { plan_id, nome, email, change_plan } = location.state || {};
 
  const pricingRef = useRef(null);  // Referência para a seção de planos

  const handleCheckoutClick = (selectedPlanName) => {
    if (change_plan && selectedPlanName === 'Free' && plan_id !== 1) {
      navigate('/login', { state: { selectedPlanName } });
    } else {
      if (change_plan) {
        navigate('/checkout', {
          state: {
            plan_id: selectedPlanName === 'Free' ? 1 : selectedPlanName === 'Basic' ? 2 : 3,
            email,
            nome,
            change_plan
          }
        });
      } else {
        navigate('/register', {
          state: {
            plan_id: selectedPlanName === 'Free' ? 1 : selectedPlanName === 'Basic' ? 2 : 3,
            change_plan
          }
        });
      }
    }
  };

  const handleLoginClick = () => {
    navigate('/login');
  };

  const isCurrentPlan = (plan) => plan_id === plan;

  // Função para rolar para a seção de planos
  const scrollToPricing = () => {
    pricingRef.current.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div>
      {/* Cabeçalho com opção de Login */}
      <header>
        <div className="header-container">
          <div className="logo-title-container">
            {/* Caminho relativo para a imagem na pasta public */}
            <h1>StockHub News</h1>
            <img src="/stockhubnews_logo.png" alt="Logo StockHub News" className="logo" />            
          </div>
          <nav>
            <ul className="nav-menu">
              <li><a href="#" onClick={handleLoginClick}>Login</a></li>
            </ul>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="hero-content">
            <div className="hero-text">
              <h2>Mantenha-se à frente no mercado de ações!</h2>
              <p>Receba notícias em tempo real das suas ações diretamente no seu email e WhatsApp. Não perca nenhuma oportunidade!</p>
              <button className="cta-button" onClick={scrollToPricing}>Experimente Grátis</button>
            </div>
            <div className="hero-image">
              {/* Caminho relativo para a imagem na pasta public */}
              <img src="/cellphone_message.png" alt="Notificações de celular" />
            </div>
          </div>
        </div>
      </section>


      {/* Seção de Benefícios */}
      <section className="benefits-section">
        <div className="container">
          <h2>Por que escolher nosso serviço?</h2>
          <ul>
            <li><span className="check-icon">✔</span> Notícias em tempo real: mantenha-se informado sobre todas as suas ações cadastradas.</li>
            <li><span className="check-icon">✔</span> Alertas personalizados: receba notificações diretamente no seu email ou WhatsApp.</li>
            <li><span className="check-icon">✔</span> Acesso a análises de sentimento: descubra o que o mercado está dizendo sobre suas ações.</li>
            <li><span className="check-icon">✔</span> Planos acessíveis para as diferentes necessidades dos investidores.</li>
          </ul>
        </div>
      </section>
      {/* Seção de comparação com e sem o  plano*/}
      <section class="comparison-section">
        <div class="container">
          <h2>Uma ferramenta obrigatória para quem leva a sério os seus investimentos</h2>
          {/* <p>Essa é a diferença entre os 99,99% dos investidores que não ganham dinheiro para os outros 0,01% que ganham</p> */}
          
          <div class="comparison-cards">
            <div class="comparison-card negative">
              <h3>Sem o StockHub News</h3>
              <ul>
                <li><FontAwesomeIcon icon={faTimesCircle} className="cross-icon"/> Buscar informação em várias fontes diferentes</li>
                <li><FontAwesomeIcon icon={faTimesCircle} className="cross-icon"/> Muito trabalho e pouco resultado</li>
                <li><FontAwesomeIcon icon={faTimesCircle} className="cross-icon"/> Poucas notícias direcionadas às suas ações</li>
                <li><FontAwesomeIcon icon={faTimesCircle} className="cross-icon"/> Não é avisado de eventos importantes das suas ações</li>
                <li><FontAwesomeIcon icon={faTimesCircle} className="cross-icon"/> Pouca informação para tomar decisões assertivas</li>
              </ul>
            </div>
            <div class="comparison-card positive">
              <h3>Com o StockHub News</h3>
              <ul>
                <li><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /> Única fonte de informações e notícias</li>
                <li><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /> Sempre atualizado de acontecimentos do mercado</li>
                <li><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /> Por dentro dos principais eventos das suas ações</li>
                <li><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /> Notícias em tempo real, por email e whatsapp</li>
                <li><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /> Alerta de recebimento de dividendos e data-com das suas ações</li>
              </ul>
            </div>
          </div>
        </div>
      </section>


      {/* Seção de Depoimentos */}
      <section className="testimonials-section">
        <div className="container">
          <h2>O que nossos usuários dizem</h2>
          <div className="testimonial">
            <p>"Desde que comecei a usar o News APP, nunca mais perdi informações importantes sobre minhas ações!"</p>
            <span>— João, Investidor Pro</span>
          </div>
          <div className="testimonial">
            <p>"As notificações em tempo real me ajudam a tomar decisões mais rápidas. Simplesmente incrível!"</p>
            <span>— Maria, Investidora Basic</span>
          </div>
        </div>
      </section>

      {/* Seção de Planos de Preço (sempre no final) */}
      <section className="pricing-section" ref={pricingRef}>
        <div className="container">
          <h2>Nossos Planos</h2>
          <table className="pricing-table">
            <thead>
              <tr>
                <th><strong>Funcionalidades</strong></th>
                <th><strong>Free</strong></th>
                <th><strong>Basic</strong></th>
                <th><strong>Pro</strong></th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Recebimento de notícias diariamente</td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
              </tr>
              <tr>
                <td>Notícias enviadas por e-mail</td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
              </tr>
              <tr>
                <td>Notícias enviadas por WhatsApp</td>
                <td>---</td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
              </tr>
              <tr>
                <td>Aviso de pagamento de dividendos por e-mail</td>
                <td>---</td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
              </tr>
              <tr>
                <td>Recebimento de notícias das suas ações em tempo real</td>
                <td>---</td>
                <td>---</td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
              </tr>
              <tr>
                <td>Análise de sentimento das suas ações</td>
                <td>---</td>
                <td>---</td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
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
              <td><strong>ESCOLHA O SEU PLANO</strong></td>
                <td>
                  <button 
                    className={`btn btn-free ${isCurrentPlan(1) ? 'current-plan' : ''}`} 
                    onClick={() => handleCheckoutClick('Free')} 
                    disabled={isCurrentPlan(1)}
                  >
                    Escolher Free
                  </button>
                </td>
                <td>
                  <button 
                    className={`btn btn-basic ${isCurrentPlan(2) ? 'current-plan' : ''}`} 
                    onClick={() => handleCheckoutClick('Basic')} 
                    disabled={isCurrentPlan(2)}
                  >
                    Escolher Basic
                  </button>
                </td>
                <td>
                  <button 
                    className={`btn btn-pro ${isCurrentPlan(3) ? 'current-plan' : ''}`} 
                    onClick={() => handleCheckoutClick('Pro')} 
                    disabled={isCurrentPlan(3)}
                  >
                    Escolher Pro
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          {/* Texto indicando "Seu plano atual" abaixo da tabela */}
          <div className="current-plan-container">
            {isCurrentPlan(1) && <span className="current-plan-label current-plan-free">Seu plano atual</span>}
            {isCurrentPlan(2) && <span className="current-plan-label current-plan-basic">Seu plano atual</span>}
            {isCurrentPlan(3) && <span className="current-plan-label current-plan-pro">Seu plano atual</span>}
          </div>
        </div>
      </section>

      {/* Rodapé */}
      <footer>
        <div className="container">
          <p>&copy; 2024 StockHub News. Todos os direitos reservados.</p>
        </div>
      </footer>
    </div>
  );
};

export default MainPage;

/* eslint-disable no-unused-vars */

import React, { useRef, useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheckCircle, faTimesCircle, faChevronDown, faChevronUp, faChevronLeft, faChevronRight } from '@fortawesome/free-solid-svg-icons';
import '../styles/MainPage.css'; // Certifique-se de que o arquivo CSS está corretamente importado

const MainPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { plan_id, nome, email, change_plan } = location.state || {};
 
  const pricingRef = useRef(null);  // Referência para a seção de planos
  const [expandedQuestion, setExpandedQuestion] = useState(null);  // Controle para expandir respostas

  const testimonials = [
    {
        text: "Desde que comecei a usar o StockHub News, nunca mais perdi informações importantes sobre minhas ações! Antes, eu precisava verificar várias fontes diferentes e muitas vezes acabava recebendo as notícias atrasadas. Agora, recebo tudo em tempo real diretamente no meu WhatsApp, o que me permite agir rapidamente. Estou extremamente satisfeito com o serviço!",
        author: "— João, Investidor Pro",
    },
    {
        text: "As notificações em tempo real me ajudam a tomar decisões mais rápidas. Simplesmente incrível! Eu costumava perder oportunidades porque não conseguia acompanhar o volume de informações que precisava analisar. O StockHub News faz todo o trabalho pesado e me envia um resumo claro e objetivo das notícias mais relevantes sobre as ações que acompanho. Recomendo muito, especialmente para quem, como eu, não tem tempo de sobra.",
        author: "— Maria, Investidora Basic",
    },
    {
        text: "O StockHub News é a melhor ferramenta que já usei para acompanhar minhas ações. Receber informações sobre dividendos e eventos relevantes de forma tão direta faz toda a diferença na minha estratégia de investimento. A simplicidade e a precisão das notificações me deram uma nova perspectiva sobre como monitorar meu portfólio. Sem dúvida, vale a pena!",
        author: "— Carlos, Investidor Free",
    },
    {
        text: "Eu estava buscando uma maneira mais eficiente de acompanhar as minhas ações, pois ficava perdido em meio a tantas informações dispersas. Com o StockHub News, eu finalmente consegui centralizar todas as atualizações e notícias mais relevantes em um só lugar. Além disso, a equipe de suporte é fantástica, sempre pronta para ajudar. Estou muito satisfeito!",
        author: "— Ana, Investidora Pro",
    },
    {
        text: "Sou novo no mundo dos investimentos e não sabia por onde começar. O StockHub News tem sido um verdadeiro guia para mim, enviando notícias que realmente importam sobre as ações que escolhi. Graças às notificações, eu me sinto muito mais confiante para tomar decisões informadas e estou aprendendo cada vez mais. Excelente serviço!",
        author: "— Rafael, Investidor Free",
    },
    {
        text: "O que mais gosto no StockHub News é a praticidade. Recebo alertas personalizados sobre os eventos que impactam diretamente as minhas ações. Isso me permite antecipar movimentos do mercado e adaptar minha estratégia de forma eficiente. Não sei como faria isso sem essa ferramenta. Para qualquer investidor que quer estar bem informado, é indispensável.",
        author: "— Beatriz, Investidora Basic",
    }
];


  const [currentTestimonial, setCurrentTestimonial] = useState(0);

  const handleNextTestimonial = () => {
    setCurrentTestimonial((prevIndex) => (prevIndex + 1) % testimonials.length);
  };

  const handlePrevTestimonial = () => {
    setCurrentTestimonial((prevIndex) => (prevIndex - 1 + testimonials.length) % testimonials.length);
  };

  // useEffect para rodar o carrossel automaticamente a cada 3 segundos
  useEffect(() => {
    const interval = setInterval(() => {
      handleNextTestimonial();
    }, 10000); 

    return () => {
      clearInterval(interval); // Limpa o intervalo quando o componente é desmontado
    };
  }, [currentTestimonial]);

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

  // Função para alternar visibilidade da resposta
  const toggleAnswer = (questionIndex) => {
    setExpandedQuestion(expandedQuestion === questionIndex ? null : questionIndex);
  };

  return (
    <div>
      {/* Cabeçalho com opção de Login */}
      <header>
        <div className="header-container">
          <div className="logo-title-container">
            <h1>StockHub News</h1>
              {/* <img src="/stockhubnews_logo.png" alt="Logo StockHub News" className="logo" />             */}
          </div>
          <nav>
            <ul className="nav-menu">
              <li><a href="#" onClick={handleLoginClick}>Login</a></li>
            </ul>
          </nav>
        </div>
      </header>

      <section className="hero-section">        
          <div className="hero-content">
            {/* Vídeo como fundo da Hero Section */}
            <video
              className="hero-video"
              src="/stock_market.mp4"
              autoPlay
              loop
              muted
              playsInline
            ></video>
            <div className="hero-text">
              <h2>Mantenha-se à frente no mercado de ações!</h2>
              <p>Receba um resumo das principais notícias das suas ações em tempo real diretamente no seu email e WhatsApp. Não perca nenhuma oportunidade!</p>
              <button className="cta-button" onClick={scrollToPricing}>Experimente Grátis</button>
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
            <li><span className="check-icon">✔</span> Utilizamos Inteligência Artificial para capturar, filtrar as principais notícias das suas ações.</li>
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


      {/* Seção de Depoimentos com Carrossel */}
      <section className="testimonials-section">
        <div className="container">
          <h2>O que nossos usuários dizem</h2>
          <div className="testimonial-carousel">
            <div className="testimonial-slider">
              <div className="testimonial-list" style={{ transform: `translateX(-${currentTestimonial * 100}%)` }}>
                {testimonials.map((testimonial, index) => (
                  <div key={index} className="testimonial-box">
                    <p>"{testimonial.text}"</p>
                    <span>{testimonial.author}</span>
                  </div>
                ))}
              </div>
            </div>
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
                <td>Recebimento diário de notícias</td>
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
                <td>Aviso de pagamento de dividendos por e-mail</td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
              </tr>
              <tr>
                <td>Recebimento de um resumo com as principais notícias das suas ações em tempo real por e-mail</td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
              </tr>
              <tr>
                <td>Notícias recebidas por WhatsApp</td>
                <td>---</td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
              </tr>
              {/* <tr>
                <td>Recebimento de um resumo com as principais notícias das suas ações em tempo real pelo whatsapp</td>
                <td>---</td>
                <td>---</td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
              </tr>               */}
              {/* <tr>
                <td>Análise de sentimento das suas ações</td>
                <td>---</td>
                <td>---</td>
                <td><FontAwesomeIcon icon={faCheckCircle} className="check-icon" /></td>
              </tr> */}
              <tr>
                <td>Quantidade de ações para cadastrar</td>
                <td>5</td>
                <td>10</td>
                <td>25</td>
              </tr>
              {/* <tr>
                <td>Quantidade de notícias recebidas</td>
                <td>2</td>
                <td>3</td>
                <td>5</td>
              </tr> */}
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

      {/* Seção de FAQ */}
      <section className="faq-section">
        <div className="container">
          <h2>Dúvidas Frequentes</h2>
          <div className="faq-item">
            <div className="faq-question" onClick={() => toggleAnswer(1)}>
              <span>Como posso me inscrever para receber as notícias em tempo real?</span>
              <FontAwesomeIcon icon={expandedQuestion === 1 ? faChevronUp : faChevronDown} />
            </div>
            {expandedQuestion === 1 && (
              <div className="faq-answer">
                <p>Basta descer até a tabela de Planos e escolher o que melhor se encaixa na sua estratégia de atualização sobre as ações do mercado brasileiro.</p>
              </div>
            )}
          </div>

          <div className="faq-item">
            <div className="faq-question" onClick={() => toggleAnswer(2)}>
              <span>Quais ações são cobertas pelas notícias enviadas?</span>
              <FontAwesomeIcon icon={expandedQuestion === 2 ? faChevronUp : faChevronDown} />
            </div>
            {expandedQuestion === 2 && (
              <div className="faq-answer">
                <p>Todas as ações listadas na B3, de empresas ativas (que ainda estão operacionais), são cobertas pelo StockHub News.</p>
              </div>
            )}
          </div>

          <div className="faq-item">
            <div className="faq-question" onClick={() => toggleAnswer(3)}>
              <span>Posso personalizar as ações que quero acompanhar?</span>
              <FontAwesomeIcon icon={expandedQuestion === 3 ? faChevronUp : faChevronDown} />
            </div>
            {expandedQuestion === 3 && (
              <div className="faq-answer">
                <p>Não. Dentro de cada plano, é possível selecionar uma quantidade máxima de ações para receber as notícias.</p>
              </div>
            )}
          </div>

          <div className="faq-item">
            <div className="faq-question" onClick={() => toggleAnswer(4)}>
              <span>Como as notícias são enviadas para o meu WhatsApp e email?</span>
              <FontAwesomeIcon icon={expandedQuestion === 4 ? faChevronUp : faChevronDown} />
            </div>
            {expandedQuestion === 4 && (
              <div className="faq-answer">
                <p>As notícias são enviadas através do seu número de WhatsApp e e-mail cadastrados, após a escolha do plano na tabela de planos.</p>
              </div>
            )}
          </div>

          <div className="faq-item">
            <div className="faq-question" onClick={() => toggleAnswer(5)}>
              <span>Com que frequência receberei notícias sobre as minhas ações?</span>
              <FontAwesomeIcon icon={expandedQuestion === 5 ? faChevronUp : faChevronDown} />
            </div>
            {expandedQuestion === 5 && (
              <div className="faq-answer">
                <p>Os planos Free e Basic permitem o recebimento de notícias ao final do pregão. No plano Pro, o recebimento das notícias começa antes do pregão iniciar e continua até o final do pregão diário da B3. Durante todo esse período, você receberá as notícias das suas ações em tempo real, tanto por e-mail quanto por WhatsApp.</p>
              </div>
            )}
          </div>

          <div className="faq-item">
            <div className="faq-question" onClick={() => toggleAnswer(6)}>
              <span>As notícias incluem informações sobre dividendos e outros eventos relevantes?</span>
              <FontAwesomeIcon icon={expandedQuestion === 6 ? faChevronUp : faChevronDown} />
            </div>
            {expandedQuestion === 6 && (
              <div className="faq-answer">
                <p>Sim, em todos os planos.</p>
              </div>
            )}
          </div>

          <div className="faq-item">
            <div className="faq-question" onClick={() => toggleAnswer(7)}>
              <span>Há algum limite de notícias que posso receber diariamente?</span>
              <FontAwesomeIcon icon={expandedQuestion === 7 ? faChevronUp : faChevronDown} />
            </div>
            {expandedQuestion === 7 && (
              <div className="faq-answer">
                <p>Sim. No plano Free, o limite é de duas notícias por ação selecionada. No plano Basic, o limite é de três notícias por ação, e no plano Pro, você pode receber até cinco notícias por ação. A quantidade mínima de notícias depende do volume de informações divulgadas sobre as suas ações pelas maiores fontes de notícias no dia.</p>
              </div>
            )}
          </div>

          <div className="faq-item">
            <div className="faq-question" onClick={() => toggleAnswer(8)}>
              <span>Posso cancelar ou modificar minha assinatura?</span>
              <FontAwesomeIcon icon={expandedQuestion === 8 ? faChevronUp : faChevronDown} />
            </div>
            {expandedQuestion === 8 && (
              <div className="faq-answer">
                <p>Sim, a qualquer momento. Após criar sua conta e escolher seu plano, o painel do seu dashboard de ações exibirá um botão "Quero mudar meu plano". Logo abaixo, estará disponível o botão "Cancelar assinatura", caso deseje encerrar sua assinatura, independentemente do plano escolhido.</p>
              </div>
            )}
          </div>

          <div className="faq-item">
            <div className="faq-question" onClick={() => toggleAnswer(9)}>
              <span>O serviço de notícias em tempo real também cobre ações internacionais?</span>
              <FontAwesomeIcon icon={expandedQuestion === 9 ? faChevronUp : faChevronDown} />
            </div>
            {expandedQuestion === 9 && (
              <div className="faq-answer">
                <p>Não, o serviço cobre apenas ações brasileiras listadas na B3.</p>
              </div>
            )}
          </div>

          <div className="faq-item">
            <div className="faq-question" onClick={() => toggleAnswer(10)}>
              <span>Quais são os planos disponíveis e as principais diferenças entre eles?</span>
              <FontAwesomeIcon icon={expandedQuestion === 10 ? faChevronUp : faChevronDown} />
            </div>
            {expandedQuestion === 10 && (
              <div className="faq-answer">
                <p>Os planos Free e Basic permitem o envio de notícias, ao final do pregão, apenas por e-mail. O plano Pro, além de permitir o envio por e-mail e WhatsApp, oferece notícias em tempo real e informações sobre fatos relevantes e dividendos anunciados pelas empresas que você selecionar.</p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Seção de Selo de Garantia */}
      <section className="guarantee-section">
        <div className="container">
          <div className="guarantee-content">
            <img src="/selo_garantia_7dias.png" alt="Selo de Qualidade e Garantia" className="guarantee-badge" />
            <div className="guarantee-text">
              <h3>Satisfação Garantida</h3>
              <p>Estamos tão confiantes na qualidade do nosso serviço que oferecemos uma <strong>garantia de 7 dias</strong>. Caso você não esteja satisfeito com o StockHub News, devolvemos o seu dinheiro.</p>
            </div>
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

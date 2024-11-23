document.getElementById('betForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = {
        valor_apostado: document.getElementById('valor_apostado').value,
        cor_apostada: document.getElementById('cor_apostada').value
    };

    fetch('/jogo_cor', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            let valorExibido = data.resultado.ganhou ? 
                data.resultado.valor_ganho : 
                parseFloat(formData.valor_apostado);

            // Verifica se é uma vitória no verde
            const isGreenWin = data.resultado.cor_sorteada === 'verde' && 
                             formData.cor_apostada === 'verde' && 
                             data.resultado.ganhou;

            // Dispara confete se ganhou no verde
            if (isGreenWin) {
                const duration = 5 * 1000;
                const animationEnd = Date.now() + duration;
                const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

                function randomInRange(min, max) {
                    return Math.random() * (max - min) + min;
                }

                const interval = setInterval(function() {
                    const timeLeft = animationEnd - Date.now();

                    if (timeLeft <= 0) {
                        return clearInterval(interval);
                    }

                    const particleCount = 50 * (timeLeft / duration);
                    
                    // Confete em posições aleatórias
                    confetti({
                        ...defaults,
                        particleCount,
                        origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
                    });
                    confetti({
                        ...defaults,
                        particleCount,
                        origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
                    });
                }, 250);
            }

            // Mostra o alerta com animação especial para verde
            Swal.fire({
                title: isGreenWin ? '🎯 MEGA WIN! 14X 🎯' : 
                       (data.resultado.ganhou ? 'Você Ganhou!' : 'Você Perdeu!'),
                html: `
                    <div style="margin-bottom: 15px;">
                        Cor sorteada: <strong>${data.resultado.cor_sorteada.toUpperCase()}</strong>
                    </div>
                    <div style="font-size: ${isGreenWin ? '1.8em' : '1.2em'}; 
                                color: ${isGreenWin ? '#10b981' : (data.resultado.ganhou ? '#10b981' : '#ef4444')};
                                font-weight: bold;
                                ${isGreenWin ? 'animation: pulse 1s infinite;' : ''}">
                        ${data.resultado.ganhou ? '+' : '-'}R$ ${valorExibido.toFixed(2)}
                    </div>
                `,
                icon: data.resultado.ganhou ? 'success' : 'error',
                confirmButtonText: 'OK',
                confirmButtonColor: '#ef4444',
                background: isGreenWin ? '#065f46' : '#1f2937',
                color: '#ffffff',
                showClass: {
                    popup: isGreenWin ? 'animate__animated animate__bounceIn' : 'swal2-show'
                }
            }).then((result) => {
                if (result.isConfirmed) {
                    document.getElementById('betForm').reset();
                    atualizarSaldo();
                    carregarHistorico();
                }
            });
            
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Erro!',
                text: data.message,
                confirmButtonText: 'OK',
                background: '#1f2937',
                color: '#ffffff'
            });
        }
    })
    .catch(error => console.error('Erro:', error));
});

// Funções auxiliares
function atualizarSaldo() {
    fetch('/get_saldo')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('saldo').textContent = 
                    `R$ ${data.saldo.toFixed(2)}`;
            }
        })
        .catch(error => console.error('Erro ao atualizar saldo:', error));
}

function carregarHistorico() {
    fetch('/get_historico_apostas')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const historicoContainer = document.querySelector('.history-container');
                historicoContainer.innerHTML = data.historico.map(aposta => {
                    // Define o valor a ser exibido
                    const valorExibido = aposta.status === 'ganhou' ? 
                        aposta.valor_ganho : 
                        aposta.valor_apostado;

                    return `
                        <div class="history-item">
                            <div class="bet-info">
                                <span class="bet-color">Cor: 
                                    <span class="color-dot ${aposta.cor_apostada}"></span>
                                    ${aposta.cor_apostada.charAt(0).toUpperCase() + aposta.cor_apostada.slice(1)}
                                </span>
                                <span class="bet-value">R$ ${aposta.valor_apostado.toFixed(2)}</span>
                            </div>
                            <div class="result-info">
                                <span class="result-color">Resultado: 
                                    <span class="color-dot ${aposta.cor_sorteada}"></span>
                                    ${aposta.cor_sorteada.charAt(0).toUpperCase() + aposta.cor_sorteada.slice(1)}
                                </span>
                                <span class="result-value ${aposta.status === 'ganhou' ? 'win' : 'loss'}">
                                    ${aposta.status === 'ganhou' ? '+' : '-'}R$ ${valorExibido.toFixed(2)}
                                </span>
                            </div>
                        </div>
                    `;
                }).join('');
            }
        })
        .catch(error => console.error('Erro ao carregar histórico:', error));
}

// Carregar histórico e saldo quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    carregarHistorico();
    atualizarSaldo();
});

// Atualizar saldo e histórico a cada 30 segundos
setInterval(() => {
    carregarHistorico();
    atualizarSaldo();
}, 30000);
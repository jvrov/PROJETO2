function updateWalletDisplay(newBalance) {
    const balanceElement = document.getElementById('userBalance');
    if (balanceElement) {
        balanceElement.textContent = `R$ ${parseFloat(newBalance).toFixed(2)}`;
        
        // Animação do valor
        balanceElement.classList.add('balance-update');
        setTimeout(() => {
            balanceElement.classList.remove('balance-update');
        }, 500);
    }
}

// Função para buscar o saldo atualizado do servidor
function fetchUpdatedBalance() {
    fetch('/get_balance')
        .then(response => response.json())
        .then(data => {
            updateWalletDisplay(data.balance);
        })
        .catch(error => console.error('Erro ao atualizar saldo:', error));
}

function atualizarSaldo() {
    fetch('/get_saldo')
        .then(response => response.json())
        .then(data => {
            const balanceElement = document.getElementById('userBalance');
            if (balanceElement) {
                const oldValue = parseFloat(balanceElement.textContent.replace('R$ ', ''));
                const newValue = parseFloat(data.saldo);
                
                if (oldValue !== newValue) {
                    balanceElement.textContent = `R$ ${newValue.toFixed(2)}`;
                    balanceElement.classList.add('updated');
                    setTimeout(() => balanceElement.classList.remove('updated'), 1000);
                }
            }
        })
        .catch(error => console.error('Erro ao atualizar saldo:', error));
} 
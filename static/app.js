const socket = io();

function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleTimeString();
}

function formatMoney(amount) {
    if (typeof amount !== 'number') {
        console.error('Invalid amount for formatMoney:', amount);
        return '$0.00';
    }
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatPercent(percent) {
    if (typeof percent !== 'number') {
        console.error('Invalid percent for formatPercent:', percent);
        return '0.00';
    }
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(percent);
}

function updateBalance(data) {
    console.log('[Client] Received balance update:', data);
    
    try {
        const totalEquity = document.getElementById('total-equity');
        const cashBalance = document.getElementById('cash-balance');
        const buyingPower = document.getElementById('buying-power');
        const hourPL = document.getElementById('hour-pl');
        const dayPL = document.getElementById('day-pl');
        const lastUpdate = document.getElementById('last-update');
        
        if (!totalEquity || !cashBalance || !buyingPower || !hourPL || !dayPL || !lastUpdate) {
            console.error('[Client] One or more balance elements not found in DOM');
            return;
        }

        totalEquity.textContent = formatMoney(data.total_equity);
        cashBalance.textContent = formatMoney(data.cash_balance);
        buyingPower.textContent = formatMoney(data.buying_power);
        
        hourPL.textContent = `${formatMoney(data.hourly_change)} (${formatPercent(data.hourly_change_pct)}%)`;
        hourPL.className = data.hourly_change >= 0 ? 'text-success' : 'text-danger';
        
        dayPL.textContent = `${formatMoney(data.daily_change)} (${formatPercent(data.daily_change_pct)}%)`;
        dayPL.className = data.daily_change >= 0 ? 'text-success' : 'text-danger';
        
        lastUpdate.textContent = `Last Update: ${data.timestamp}`;
        
        console.log('[Client] Balance update successful');
    } catch (error) {
        console.error('[Client] Error updating balance:', error);
    }
}

function addLogEntry(data) {
    console.log('[Client] Received log message:', data);
    try {
        const logContainer = document.getElementById('log-container');
        if (!logContainer) {
            console.error('[Client] Log container not found');
            return;
        }
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.innerHTML = `
            <span class="timestamp">[${formatTimestamp(data.timestamp)}]</span>
            <span>${data.message}</span>
        `;
        logContainer.appendChild(entry);
        logContainer.scrollTop = logContainer.scrollHeight;
    } catch (error) {
        console.error('[Client] Error adding log entry:', error);
    }
}

function updateTrade(data) {
    console.log('[Client] Received trade update:', data);
    try {
        const tradesContainer = document.getElementById('trades-container');
        if (!tradesContainer) {
            console.error('[Client] Trades container not found');
            return;
        }
        const tradeId = `trade-${data.symbol}`;
        let tradeElement = document.getElementById(tradeId);
        
        if (!tradeElement) {
            tradeElement = document.createElement('div');
            tradeElement.id = tradeId;
            tradeElement.className = `trade-entry ${data.action}`;
            tradesContainer.appendChild(tradeElement);
        }
        
        tradeElement.innerHTML = `
            <strong>${data.symbol}</strong>
            <div>Action: ${data.action.toUpperCase()}</div>
            <div>Price: ${formatMoney(data.price)}</div>
            <div>Quantity: ${data.quantity}</div>
            <div class="timestamp">${formatTimestamp(data.timestamp)}</div>
        `;
    } catch (error) {
        console.error('[Client] Error updating trade:', error);
    }
}

// Socket event listeners
socket.on('connect', () => {
    console.log('[Client] Connected to server');
    socket.emit('request_balance');
});

socket.on('disconnect', () => {
    console.log('[Client] Disconnected from server');
});

socket.on('log_message', (data) => {
    console.log('[Client] Received log message event');
    addLogEntry(data);
});

socket.on('trade_update', (data) => {
    console.log('[Client] Received trade update event');
    updateTrade(data);
});

socket.on('balance_update', (data) => {
    console.log('[Client] Received balance update event');
    updateBalance(data);
});

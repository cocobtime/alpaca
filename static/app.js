const socket = io({
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: Infinity
});

// Chart.js configuration
let equityChart = null;
const equityData = {
    labels: [],
    values: []
};

function initializeChart() {
    const ctx = document.getElementById('equity-chart').getContext('2d');
    equityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: equityData.labels,
            datasets: [{
                label: 'Total Equity',
                data: equityData.values,
                borderColor: '#2c3e50',
                backgroundColor: 'rgba(44, 62, 80, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    display: false
                },
                y: {
                    display: true,
                    grid: {
                        display: false
                    }
                }
            },
            animation: {
                duration: 750,
                easing: 'easeInOutQuart'
            }
        }
    });
}

function updateEquityChart(value) {
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    
    equityData.labels.push(timeStr);
    equityData.values.push(value);
    
    // Keep only last 20 data points
    if (equityData.labels.length > 20) {
        equityData.labels.shift();
        equityData.values.shift();
    }
    
    if (equityChart) {
        equityChart.update('none');
    }
}

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

function updateProgressBar(elementId, value) {
    const bar = document.getElementById(elementId);
    const percentage = Math.min(Math.abs(value), 100);
    bar.style.width = `${percentage}%`;
    bar.className = `progress-bar ${value >= 0 ? 'positive' : 'negative'}`;
}

function updateBalance(data) {
    console.log('[Client] Received balance update:', data);
    
    try {
        if (!data) {
            console.error('[Client] Invalid balance data received');
            return;
        }

        // Update main balance displays
        document.getElementById('total-equity').textContent = formatMoney(data.total_equity || 0);
        document.getElementById('cash-balance').textContent = formatMoney(data.cash_balance || 0);
        document.getElementById('buying-power').textContent = `Buying Power: ${formatMoney(data.buying_power || 0)}`;
        
        // Update market status
        const marketStatus = document.getElementById('market-status');
        if (marketStatus) {
            marketStatus.innerHTML = data.is_market_open ? 
                '<i class="fas fa-circle text-success me-2"></i>Market Open' :
                '<i class="fas fa-circle text-danger me-2"></i>Market Closed';
        }
        
        // Update P/L displays with progress bars
        const hourPL = document.getElementById('hour-pl');
        const hourlyChange = data.hourly_change || 0;
        const hourlyChangePct = data.hourly_change_pct || 0;
        hourPL.textContent = `${formatMoney(hourlyChange)} (${formatPercent(hourlyChangePct)}%)`;
        hourPL.className = hourlyChange >= 0 ? 'text-success' : 'text-danger';
        updateProgressBar('hour-pl-bar', hourlyChangePct);
        
        const dayPL = document.getElementById('day-pl');
        const dailyChange = data.daily_change || 0;
        const dailyChangePct = data.daily_change_pct || 0;
        dayPL.textContent = `${formatMoney(dailyChange)} (${formatPercent(dailyChangePct)}%)`;
        dayPL.className = dailyChange >= 0 ? 'text-success' : 'text-danger';
        updateProgressBar('day-pl-bar', dailyChangePct);
        
        // Update chart
        updateEquityChart(data.total_equity || 0);
        
        // Update timestamp
        document.getElementById('last-update').textContent = `Last Update: ${data.timestamp || 'Unknown'}`;
        
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
            <span class="message">${data.message}</span>
        `;
        
        logContainer.appendChild(entry);
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // Keep only last 100 log entries
        while (logContainer.children.length > 100) {
            logContainer.removeChild(logContainer.firstChild);
        }
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
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>${data.symbol}</strong>
                    <span class="badge ${data.action === 'buy' ? 'bg-success' : 'bg-danger'} ms-2">
                        ${data.action.toUpperCase()}
                    </span>
                </div>
                <div class="text-end">
                    <div>${formatMoney(data.price)}</div>
                    <small class="text-muted">${data.quantity} shares</small>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('[Client] Error updating trade:', error);
    }
}

// Initialize UI elements
document.addEventListener('DOMContentLoaded', () => {
    initializeChart();
    
    // Trade view filters
    document.getElementById('view-all').addEventListener('click', () => {
        document.querySelectorAll('.trade-entry').forEach(el => el.style.display = 'block');
    });
    
    document.getElementById('view-buy').addEventListener('click', () => {
        document.querySelectorAll('.trade-entry').forEach(el => {
            el.style.display = el.classList.contains('buy') ? 'block' : 'none';
        });
    });
    
    document.getElementById('view-sell').addEventListener('click', () => {
        document.querySelectorAll('.trade-entry').forEach(el => {
            el.style.display = el.classList.contains('sell') ? 'block' : 'none';
        });
    });
    
    // Clear log button
    document.getElementById('clear-log').addEventListener('click', () => {
        document.getElementById('log-container').innerHTML = '';
    });
});

// Socket event listeners
socket.on('connect', () => {
    console.log('[Client] Connected to server');
    document.getElementById('connection-status').innerHTML = '<i class="fas fa-circle text-success me-2"></i>Connected';
    // Request initial balance update
    socket.emit('get_balance');
});

socket.on('disconnect', () => {
    console.log('[Client] Disconnected from server');
    document.getElementById('connection-status').innerHTML = '<i class="fas fa-circle text-danger me-2"></i>Disconnected';
});

socket.on('connect_error', (error) => {
    console.error('[Client] Connection error:', error);
    document.getElementById('connection-status').innerHTML = '<i class="fas fa-circle text-warning me-2"></i>Connecting...';
});

socket.on('balance_update', updateBalance);
socket.on('trade_update', updateTrade);
socket.on('log_message', addLogEntry);

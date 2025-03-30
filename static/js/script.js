// Configuração da instância
const INSTANCE_ID = 'i-05249f744fa92653c';
const REGION = 'sa-east-1';
const KEY_PAIR_NAME = 'MyInstance';

// Configuração dos gráficos
let cpuChart, memoryChart, diskChart, networkChart;
let timeRange = 1; // Horas padrão
let updateInterval = 300000; // 5 minutos

// Função para formatar bytes em MB
function formatBytes(bytes) {
    return (bytes / 1024 / 1024).toFixed(2) + ' MB';
}

// Função para formatar porcentagem
function formatPercentage(value) {
    return value.toFixed(2) + '%';
}

// Função para criar ou atualizar um gráfico
function updateChart(chart, data, label, color, formatValue) {
    const ctx = chart.ctx;
    const config = chart.config;
    
    config.data.labels = data.map(point => point.formatted_timestamp);
    config.data.datasets[0].data = data.map(point => point.value);
    config.data.datasets[0].label = label;
    config.data.datasets[0].borderColor = color;
    config.data.datasets[0].backgroundColor = color + '20';
    
    config.options.scales.y.ticks.callback = function(value) {
        return formatValue(value);
    };
    
    chart.update('none');
}

// Função para atualizar as informações da instância
async function updateInstanceInfo() {
    try {
        const response = await fetch(`/api/instance/${INSTANCE_ID}`);
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.message);
        }
        
        document.getElementById('instance-id').textContent = data.id;
        document.getElementById('instance-state').textContent = data.state;
        document.getElementById('instance-type').textContent = data.type;
        document.getElementById('instance-dns').textContent = data.public_dns;
        document.getElementById('instance-ip').textContent = data.public_ip;
        
        // Atualiza o comando SSH
        const sshCommand = document.getElementById('ssh-command');
        sshCommand.value = data.ssh_command;
        
        // Atualiza as tags
        const tagsContainer = document.getElementById('instance-tags');
        tagsContainer.innerHTML = '';
        if (data.tags && data.tags.length > 0) {
            data.tags.forEach(tag => {
                const tagElement = document.createElement('span');
                tagElement.className = 'tag';
                tagElement.textContent = `${tag.Key}: ${tag.Value}`;
                tagsContainer.appendChild(tagElement);
            });
        } else {
            tagsContainer.innerHTML = '<span class="tag">Nenhuma tag</span>';
        }
        
    } catch (error) {
        console.error('Erro ao obter informações da instância:', error);
        showError('Erro ao carregar informações da instância: ' + error.message);
    }
}

// Função para atualizar as métricas
async function updateMetrics() {
    try {
        const response = await fetch(`/api/metrics/${INSTANCE_ID}?hours=${timeRange}`);
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.message);
        }
        
        // Atualiza os gráficos
        if (data.cpu && data.cpu.length > 0) {
            updateChart(cpuChart, data.cpu, 'CPU', '#FF6B6B', formatPercentage);
            document.getElementById('cpu-value').textContent = formatPercentage(data.cpu[data.cpu.length - 1].value);
        }
        
        if (data.memory && data.memory.length > 0) {
            updateChart(memoryChart, data.memory, 'Memória', '#4ECDC4', formatPercentage);
            document.getElementById('memory-value').textContent = formatPercentage(data.memory[data.memory.length - 1].value);
        }
        
        if (data.disk && data.disk.length > 0) {
            updateChart(diskChart, data.disk, 'Disco', '#45B7D1', formatPercentage);
            document.getElementById('disk-value').textContent = formatPercentage(data.disk[data.disk.length - 1].value);
        }
        
        if (data.network && data.network.length > 0) {
            const lastNetwork = data.network[data.network.length - 1];
            updateChart(networkChart, data.network.map(point => ({
                ...point,
                value: point.in_mb + point.out_mb
            })), 'Rede', '#96CEB4', formatBytes);
            document.getElementById('network-in-value').textContent = formatBytes(lastNetwork.in);
            document.getElementById('network-out-value').textContent = formatBytes(lastNetwork.out);
        }
        
    } catch (error) {
        console.error('Erro ao obter métricas:', error);
        showError('Erro ao carregar métricas: ' + error.message);
    }
}

// Função para exibir mensagens de erro
function showError(message) {
    const errorContainer = document.getElementById('error-container');
    errorContainer.innerHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            <span>${message}</span>
        </div>
    `;
    errorContainer.style.display = 'block';
    
    // Esconde a mensagem após 5 segundos
    setTimeout(() => {
        errorContainer.style.display = 'none';
    }, 5000);
}

// Função para copiar o comando SSH
function copySSHCommand() {
    const sshCommand = document.getElementById('ssh-command');
    sshCommand.select();
    document.execCommand('copy');
    
    // Feedback visual
    const button = document.getElementById('copy-ssh');
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-check"></i> Copiado!';
    setTimeout(() => {
        button.innerHTML = originalText;
    }, 2000);
}

// Função para atualizar o intervalo de tempo
function updateTimeRange(hours) {
    timeRange = hours;
    updateMetrics();
}

// Inicialização dos gráficos
document.addEventListener('DOMContentLoaded', function() {
    // Configuração dos gráficos
    const chartConfig = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                data: [],
                borderWidth: 2,
                fill: true,
                tension: 0.4
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
                    display: true,
                    title: {
                        display: true,
                        text: 'Tempo'
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Valor'
                    }
                }
            }
        }
    };
    
    // Inicializa os gráficos
    cpuChart = new Chart(document.getElementById('cpu-chart'), chartConfig);
    memoryChart = new Chart(document.getElementById('memory-chart'), chartConfig);
    diskChart = new Chart(document.getElementById('disk-chart'), chartConfig);
    networkChart = new Chart(document.getElementById('network-chart'), chartConfig);
    
    // Atualiza os dados inicialmente
    updateInstanceInfo();
    updateMetrics();
    
    // Configura atualização automática
    setInterval(updateInstanceInfo, updateInterval);
    setInterval(updateMetrics, updateInterval);
}); 
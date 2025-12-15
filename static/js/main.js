let cpuChart, memoryChart, diskChart;
let cpuData = [], memoryData = [], diskData = [];
const maxDataPoints = 20;

document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    loadSystemInfo();
    loadProcesses();
    loadNetwork();

    // Refresh data every 5 seconds
    setInterval(() => {
        loadSystemInfo();
        loadProcesses();
        loadNetwork();
    }, 5000);

    document.getElementById('shutdown-btn').addEventListener('click', function() {
        if (confirm('Are you sure you want to shutdown the system?')) {
            performAction('/api/shutdown');
        }
    });

    document.getElementById('restart-btn').addEventListener('click', function() {
        if (confirm('Are you sure you want to restart the system?')) {
            performAction('/api/restart');
        }
    });

    document.getElementById('restart-service-btn').addEventListener('click', function() {
        const service = document.getElementById('service-name').value;
        if (!service) {
            alert('Please enter a service name');
            return;
        }
        if (confirm(`Restart service ${service}?`)) {
            fetch('/api/restart_service', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ service })
            })
            .then(response => response.json())
            .then(data => alert(data.message));
        }
    });

    document.getElementById('status-service-btn').addEventListener('click', function() {
        const service = document.getElementById('service-name').value;
        if (!service) {
            alert('Please enter a service name');
            return;
        }
        fetch('/api/service_status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ service })
        })
        .then(response => response.json())
        .then(data => alert(data.message));
    });

    document.getElementById('run-command-btn').addEventListener('click', function() {
        const command = document.getElementById('command-input').value;
        if (!command) {
            alert('Please enter a command');
            return;
        }
        fetch('/api/run_command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command })
        })
        .then(response => response.json())
        .then(data => {
            const outputDiv = document.getElementById('command-output');
            const resultPre = document.getElementById('command-result');
            if (data.status === 'success') {
                resultPre.textContent = data.output;
                outputDiv.style.display = 'block';
            } else {
                alert(data.message);
            }
        });
    });

    document.getElementById('view-logs-btn').addEventListener('click', function() {
        fetch('/api/view_logs')
        .then(response => response.json())
        .then(data => {
            const outputDiv = document.getElementById('logs-output');
            const resultPre = document.getElementById('logs-result');
            if (data.status === 'success') {
                resultPre.textContent = data.logs;
                outputDiv.style.display = 'block';
            } else {
                alert(data.message);
            }
        });
    });
});

function initCharts() {
    const ctxCpu = document.getElementById('cpuChart').getContext('2d');
    cpuChart = new Chart(ctxCpu, {
        type: 'line',
        data: {
            labels: Array(maxDataPoints).fill(''),
            datasets: [{
                label: 'CPU %',
                data: cpuData,
                borderColor: 'rgba(40, 42, 160, 1)',
                backgroundColor: 'rgba(99, 203, 255, 0.2)',
                fill: true,
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, max: 100 }
            }
        }
    });

    const ctxMemory = document.getElementById('memoryChart').getContext('2d');
    memoryChart = new Chart(ctxMemory, {
        type: 'doughnut',
        data: {
            labels: ['Used', 'Free'],
            datasets: [{
                data: [0, 100],
                backgroundColor: ['rgba(54, 162, 235, 0.8)', 'rgba(54, 162, 235, 0.2)'],
            }]
        },
        options: {
            responsive: true,
        }
    });

    const ctxDisk = document.getElementById('diskChart').getContext('2d');
    diskChart = new Chart(ctxDisk, {
        type: 'doughnut',
        data: {
            labels: ['Used', 'Free'],
            datasets: [{
                data: [0, 100],
                backgroundColor: ['rgba(255, 205, 86, 0.8)', 'rgba(255, 205, 86, 0.2)'],
            }]
        },
        options: {
            responsive: true,
        }
    });
}

function loadSystemInfo() {
    fetch('/api/system_info')
        .then(response => response.json())
        .then(data => {
            // Update text
            document.getElementById('cpu-text').textContent = data.cpu.toFixed(1);
            document.getElementById('memory-text').textContent = data.memory.percent.toFixed(1);
            document.getElementById('memory-used').textContent = data.memory.used;
            document.getElementById('memory-total').textContent = data.memory.total;
            document.getElementById('disk-text').textContent = data.disk.percent.toFixed(1);
            document.getElementById('disk-used').textContent = data.disk.used;
            document.getElementById('disk-total').textContent = data.disk.total;
            document.getElementById('uptime').textContent = data.uptime;

            // Update charts
            updateCpuChart(data.cpu);
            updateMemoryChart(data.memory.percent);
            updateDiskChart(data.disk.percent);
        })
        .catch(error => console.error('Error loading system info:', error));
}

function updateCpuChart(cpu) {
    cpuData.push(cpu);
    if (cpuData.length > maxDataPoints) cpuData.shift();
    cpuChart.data.datasets[0].data = cpuData;
    cpuChart.update();
}

function updateMemoryChart(memoryPercent) {
    memoryChart.data.datasets[0].data = [memoryPercent, 100 - memoryPercent];
    memoryChart.update();
}

function updateDiskChart(diskPercent) {
    diskChart.data.datasets[0].data = [diskPercent, 100 - diskPercent];
    diskChart.update();
}

function loadProcesses() {
    fetch('/api/processes')
        .then(response => response.json())
        .then(data => {
            console.log('Processes data:', data);
            const tbody = document.getElementById('processes-body');
            tbody.innerHTML = '';
            data.forEach(proc => {
                const row = `<tr>
                    <td>${proc.pid}</td>
                    <td>${proc.name}</td>
                    <td>${proc.cpu.toFixed(1)}</td>
                    <td>${proc.memory.toFixed(1)}</td>
                </tr>`;
                tbody.innerHTML += row;
            });
        })
        .catch(error => console.error('Error loading processes:', error));
}

function loadNetwork() {
    fetch('/api/network')
        .then(response => response.json())
        .then(data => {
            document.getElementById('net-sent').textContent = data.sent + ' MB';
            document.getElementById('net-recv').textContent = data.recv + ' MB';
            document.getElementById('net-connections').textContent = data.connections;
        })
        .catch(error => console.error('Error loading network:', error));
}

function performAction(endpoint) {
    fetch(endpoint, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => console.error('Error performing action:', error));
}
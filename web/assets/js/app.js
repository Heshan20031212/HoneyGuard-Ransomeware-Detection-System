/**
 * HoneyGuard Web Portal - Interactive Frontend Application
 */

document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    setupLivePolling();
    animateCounters();
});

function animateCounters() {
    const counters = document.querySelectorAll('.stat-value');
    counters.forEach(counter => {
        const raw = counter.innerText.replace(/,/g, '').trim();
        const target = parseFloat(raw);
        if (isNaN(target) || target === 0) return;

        let current = 0;
        const duration = 900; // ms
        const steps = 25;
        const stepTime = duration / steps;
        const increment = target / steps;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                counter.innerText = Math.round(target).toLocaleString();
                clearInterval(timer);
            } else {
                counter.innerText = Math.round(current).toLocaleString();
            }
        }, stepTime);
    });
}

function initCharts() {
    // 1. Severity Distribution Doughnut Chart
    const severityCanvas = document.getElementById('severityChart');
    if (severityCanvas && typeof Chart !== 'undefined') {
        const crit = parseInt(severityCanvas.dataset.crit || 0);
        const high = parseInt(severityCanvas.dataset.high || 0);
        const med  = parseInt(severityCanvas.dataset.med || 0);
        const low  = parseInt(severityCanvas.dataset.low || 0);

        new Chart(severityCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{
                    data: [crit, high, med, low],
                    backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#10b981'],
                    borderColor: '#111827',
                    borderWidth: 3,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 12 } }
                    }
                },
                cutout: '68%'
            }
        });
    }

    // 2. File Events Velocity Chart
    const velocityCanvas = document.getElementById('velocityChart');
    if (velocityCanvas && typeof Chart !== 'undefined') {
        const labels = JSON.parse(velocityCanvas.dataset.labels || '[]');
        const values = JSON.parse(velocityCanvas.dataset.values || '[]');

        new Chart(velocityCanvas, {
            type: 'line',
            data: {
                labels: labels.length ? labels : ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', 'Now'],
                datasets: [{
                    label: 'Filesystem Activity (Events/Min)',
                    data: values.length ? values : [5, 12, 18, 45, 95, 30, 15],
                    borderColor: '#06b6d4',
                    backgroundColor: 'rgba(6, 182, 212, 0.1)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 2,
                    pointBackgroundColor: '#06b6d4',
                    pointRadius: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#64748b', font: { size: 11 } }
                    },
                    y: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#64748b', font: { size: 11 } }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
}

function setupLivePolling() {
    const liveSwitch = document.getElementById('liveAutoRefresh');
    if (liveSwitch) {
        let interval = null;
        liveSwitch.addEventListener('change', (e) => {
            if (e.target.checked) {
                interval = setInterval(() => {
                    location.reload();
                }, 5000);
            } else {
                if (interval) clearInterval(interval);
            }
        });
    }
}

function openModal(id) {
    const m = document.getElementById(id);
    if (m) m.classList.add('active');
}

function closeModal(id) {
    const m = document.getElementById(id);
    if (m) m.classList.remove('active');
}

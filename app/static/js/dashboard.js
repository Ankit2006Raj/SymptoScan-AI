document.addEventListener('DOMContentLoaded', () => {
    fetchDashboardStats();
});

async function fetchDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        const data = await response.json();
        
        if (data.success) {
            renderTimeline(data.timeline);
            renderKPIs(data.timeline);
            renderChart(data.timeline);
        }
    } catch (e) {
        console.error("Failed to load dashboard stats", e);
    }
}

function renderTimeline(timeline) {
    const container = document.getElementById('timeline-container');
    container.innerHTML = '';
    
    if (timeline.length === 0) {
        container.innerHTML = '<div class="text-center py-10 text-slate-400 text-sm ml-[-12px]">No activity found yet.</div>';
        return;
    }

    timeline.forEach(item => {
        let icon = '';
        let color = '';
        let exportBtn = '';

        if (item.type === 'medical_report') {
            icon = 'fa-file-medical';
            color = 'bg-blue-500';
            exportBtn = `<a href="/api/export-report/medical_report/${item.id}" target="_blank" class="mt-2 text-xs text-primary font-bold hover:underline flex items-center gap-1"><i class="fa-solid fa-download"></i> Download PDF</a>`;
        } else if (item.type === 'risk_prediction') {
            icon = 'fa-heart-pulse';
            color = 'bg-red-500';
            exportBtn = `<a href="/api/export-report/risk_prediction/${item.id}" target="_blank" class="mt-2 text-xs text-primary font-bold hover:underline flex items-center gap-1"><i class="fa-solid fa-download"></i> Download PDF</a>`;
        } else {
            icon = 'fa-stethoscope';
            color = 'bg-emerald-500';
        }

        const html = `
            <div class="relative pl-6">
                <div class="absolute -left-2 top-0.5 w-4 h-4 rounded-full ${color} border-2 border-white shadow-sm"></div>
                <div class="mb-1 text-xs font-bold text-slate-400">${item.date}</div>
                <div class="text-sm font-bold text-slate-800 bg-slate-50 p-3 rounded-xl border border-slate-100 flex flex-col items-start gap-1">
                    <div class="flex items-center gap-2"><i class="fa-solid ${icon} text-slate-400"></i> ${item.title}</div>
                    ${exportBtn}
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', html);
    });
}

function renderKPIs(timeline) {
    const reports = timeline.filter(t => t.type === 'medical_report').length;
    const risks = timeline.filter(t => t.type === 'risk_prediction').length;
    const symptoms = timeline.filter(t => t.type === 'symptom_assessment').length;
    
    document.getElementById('kpi-reports').textContent = reports;
    document.getElementById('kpi-risks').textContent = risks;
    document.getElementById('kpi-symptoms').textContent = symptoms;
}

function renderChart(timeline) {
    const ctx = document.getElementById('activityChart');
    if (!ctx) return;
    
    // Simple mock data for aesthetic purposes based on actual counts
    const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    const dataPts = [1, 3, 2, 5, 4, timeline.length];

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Interactions',
                data: dataPts,
                backgroundColor: '#3b82f6',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { borderDash: [5,5] } },
                x: { grid: { display: false } }
            }
        }
    });
}

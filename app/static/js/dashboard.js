document.addEventListener('DOMContentLoaded', () => {
    fetchDashboardAnalytics();
});

let chartInstances = {};

async function fetchDashboardAnalytics() {
    try {
        const response = await fetch('/api/analytics/dashboard');
        const data = await response.json();
        
        if (data.success) {
            updateKPIs(data.kpis);
            updateAISummaries(data.ai_summaries);
            renderCharts(data.charts);
            renderTimeline(data.timeline);
        } else {
            console.error("Dashboard error:", data.error);
        }
    } catch (e) {
        console.error("Failed to load dashboard stats", e);
    }
}

function updateKPIs(kpis) {
    document.getElementById('kpi-total').textContent = kpis.total_assessments || 0;
    document.getElementById('kpi-score').textContent = `${kpis.avg_health_score || 0}/100`;
    document.getElementById('kpi-reports').textContent = kpis.reports_generated || 0;
    document.getElementById('kpi-alerts').textContent = kpis.active_alerts || 0;
}

function updateAISummaries(summaries) {
    document.getElementById('ai-symptom').textContent = summaries.frequent_symptom;
    document.getElementById('ai-risk').textContent = summaries.highest_risk;
    document.getElementById('ai-trend').textContent = summaries.improvement_trend;
    document.getElementById('ai-action').textContent = summaries.next_action;
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
        let bgLight = '';
        let exportBtn = '';

        if (item.type === 'medical_report') {
            icon = 'fa-file-medical';
            color = 'border-blue-500';
            bgLight = 'bg-blue-50';
            exportBtn = `<a href="/api/export-report/medical_report/${item.id}" target="_blank" class="mt-3 text-xs text-blue-600 font-bold hover:text-blue-800 transition flex items-center gap-1.5 px-3 py-1.5 bg-blue-100/50 rounded-lg w-max"><i class="fa-solid fa-download"></i> Download PDF</a>`;
        } else if (item.type === 'risk_prediction') {
            icon = 'fa-heart-pulse';
            color = 'border-red-500';
            bgLight = 'bg-red-50';
            exportBtn = `<a href="/api/export-report/risk_prediction/${item.id}" target="_blank" class="mt-3 text-xs text-red-600 font-bold hover:text-red-800 transition flex items-center gap-1.5 px-3 py-1.5 bg-red-100/50 rounded-lg w-max"><i class="fa-solid fa-download"></i> Download PDF</a>`;
        } else {
            icon = 'fa-stethoscope';
            color = 'border-emerald-500';
            bgLight = 'bg-emerald-50';
        }

        const html = `
            <div class="relative pl-6 group transition-all duration-300 hover:pl-8">
                <div class="absolute -left-[9px] top-1.5 w-4 h-4 rounded-full bg-white ${color} border-4 shadow-sm group-hover:scale-125 transition-transform"></div>
                <div class="mb-1 text-[11px] font-bold text-slate-400 uppercase tracking-wider">${item.date}</div>
                <div class="text-sm text-slate-700 ${bgLight} p-4 rounded-xl border border-slate-100 shadow-sm flex flex-col items-start gap-1 group-hover:shadow-md transition-shadow">
                    <div class="font-bold flex items-center gap-2"><i class="fa-solid ${icon} opacity-50"></i> ${item.title}</div>
                    ${exportBtn}
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', html);
    });
}

function renderCharts(chartsData) {
    // Shared chart options
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: { font: { family: "'Inter', sans-serif", size: 12 }, usePointStyle: true, padding: 20 }
            },
            tooltip: {
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                titleFont: { family: "'Inter', sans-serif", size: 13 },
                bodyFont: { family: "'Inter', sans-serif", size: 13 },
                padding: 12,
                cornerRadius: 8,
                displayColors: true
            }
        }
    };

    // 1. Health Trends (Line)
    const ctxTrends = document.getElementById('healthTrendsChart');
    if (ctxTrends) {
        if(chartInstances.trends) chartInstances.trends.destroy();
        chartInstances.trends = new Chart(ctxTrends, {
            type: 'line',
            data: {
                labels: chartsData.health_trends.labels,
                datasets: [{
                    label: 'Assessments',
                    data: chartsData.health_trends.data,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: '#3b82f6',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                ...commonOptions,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { borderDash: [4, 4], color: '#f1f5f9' }, border: { display: false } },
                    x: { grid: { display: false }, border: { display: false } }
                }
            }
        });
    }

    // 2. Risk Distribution (Doughnut)
    const ctxRisk = document.getElementById('riskDistChart');
    if (ctxRisk) {
        if(chartInstances.risk) chartInstances.risk.destroy();
        chartInstances.risk = new Chart(ctxRisk, {
            type: 'doughnut',
            data: {
                labels: chartsData.risk_distribution.labels,
                datasets: [{
                    data: chartsData.risk_distribution.data,
                    backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                ...commonOptions,
                cutout: '70%',
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    // 3. Common Symptoms (Bar)
    const ctxSymptoms = document.getElementById('symptomsChart');
    if (ctxSymptoms) {
        if(chartInstances.symptoms) chartInstances.symptoms.destroy();
        chartInstances.symptoms = new Chart(ctxSymptoms, {
            type: 'bar',
            data: {
                labels: chartsData.common_symptoms.labels,
                datasets: [{
                    label: 'Frequency',
                    data: chartsData.common_symptoms.data,
                    backgroundColor: '#8b5cf6',
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                ...commonOptions,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { borderDash: [4, 4], color: '#f1f5f9' }, border: { display: false } },
                    x: { grid: { display: false }, border: { display: false } }
                }
            }
        });
    }

    // 4. Disease Categories (Bar/Horizontal)
    const ctxDisease = document.getElementById('diseaseCategoryChart');
    if (ctxDisease) {
        if(chartInstances.disease) chartInstances.disease.destroy();
        chartInstances.disease = new Chart(ctxDisease, {
            type: 'bar',
            data: {
                labels: chartsData.disease_categories.labels,
                datasets: [{
                    label: 'Predictions',
                    data: chartsData.disease_categories.data,
                    backgroundColor: ['#3b82f6', '#ec4899', '#06b6d4', '#f59e0b', '#8b5cf6'],
                    borderRadius: 6
                }]
            },
            options: {
                ...commonOptions,
                indexAxis: 'y', // horizontal bar
                plugins: { legend: { display: false } },
                scales: {
                    x: { beginAtZero: true, grid: { borderDash: [4, 4], color: '#f1f5f9' }, border: { display: false } },
                    y: { grid: { display: false }, border: { display: false } }
                }
            }
        });
    }
}

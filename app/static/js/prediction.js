document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('prediction-form');
    if (!form) return;

    const diseaseType = form.getAttribute('data-disease');
    const submitBtn = document.getElementById('submit-btn');
    const resultsDashboard = document.getElementById('results-dashboard');
    
    // Result Elements
    const riskScoreValue = document.getElementById('risk-score-value');
    const riskCategoryBadge = document.getElementById('risk-category-badge');
    const factorsList = document.getElementById('factors-list');
    const recsList = document.getElementById('recs-list');
    
    // Chart instances
    let gaugeChartInstance = null;
    let trendChartInstance = null;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // 1. Gather Data
        const formData = {};
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            if (input.type === 'radio') {
                if (input.checked) {
                    formData[input.name] = input.value;
                }
            } else if (input.id) {
                formData[input.id] = input.value;
            }
        });

        // UI Loading State
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Analyzing...';
        submitBtn.disabled = true;

        try {
            // 2. Make API Call
            const response = await fetch(`/api/predict/${diseaseType}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Prediction failed');
            }

            // 3. Display Results
            renderResults(data.results);
            
        } catch (error) {
            alert('Error: ' + error.message);
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    });

    function renderResults(results) {
        if (diseaseType === 'comprehensive') {
            renderComprehensiveResults(results);
            return;
        }

        // Show dashboard
        resultsDashboard.classList.remove('hidden');
        
        // Update texts
        const score = results.risk_score;
        riskScoreValue.textContent = `${score}%`;
        riskCategoryBadge.textContent = `${results.risk_category} RISK`;
        
        // Color badge based on category
        const cat = results.risk_category.toLowerCase();
        if (cat === 'low') {
            riskCategoryBadge.className = "text-xs font-bold uppercase tracking-widest text-green-500 mt-1";
        } else if (cat === 'moderate') {
            riskCategoryBadge.className = "text-xs font-bold uppercase tracking-widest text-amber-500 mt-1";
        } else {
            riskCategoryBadge.className = "text-xs font-bold uppercase tracking-widest text-red-500 mt-1";
        }

        // Factors
        factorsList.innerHTML = '';
        if (results.factors && results.factors.length > 0) {
            results.factors.forEach(f => {
                factorsList.insertAdjacentHTML('beforeend', `<li class="text-sm text-slate-700 flex items-start gap-2"><i class="fa-solid fa-angle-right text-slate-400 mt-1"></i> ${f}</li>`);
            });
        } else {
            factorsList.innerHTML = '<li class="text-sm text-slate-500">No major risk factors detected based on inputs.</li>';
        }

        // Recommendations
        recsList.innerHTML = '';
        if (results.recommendations) {
            results.recommendations.forEach(r => {
                recsList.insertAdjacentHTML('beforeend', `<li class="text-sm text-slate-700 flex items-start gap-2"><i class="fa-solid fa-circle-check text-secondary mt-1"></i> ${r}</li>`);
            });
        }

        // Render Charts
        renderGaugeChart(score, cat);
        renderTrendChart(score);
        
        // Scroll to results
        resultsDashboard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function renderGaugeChart(score, category) {
        const ctx = document.getElementById('gaugeChart').getContext('2d');
        
        if (gaugeChartInstance) {
            gaugeChartInstance.destroy();
        }

        let color = '#2563EB'; // primary
        if (category.toLowerCase() === 'high') color = '#ef4444';
        else if (category.toLowerCase() === 'moderate') color = '#f59e0b';
        else if (category.toLowerCase() === 'low') color = '#10b981';

        gaugeChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [score, 100 - score],
                    backgroundColor: [color, '#f1f5f9'],
                    borderWidth: 0,
                    circumference: 250,
                    rotation: 235,
                    cutout: '80%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    tooltip: { enabled: false },
                    legend: { display: false }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            }
        });
    }

    function renderTrendChart(latestScore) {
        const ctx = document.getElementById('trendChart').getContext('2d');
        
        if (trendChartInstance) {
            trendChartInstance.destroy();
        }

        // Generate mock historical data ending with the new latest score
        // In a real app, this data would come from the database history for the user
        const historicalScores = [
            Math.max(0, latestScore - 15),
            Math.max(0, latestScore - 5),
            Math.max(0, latestScore + 10),
            Math.max(0, latestScore - 2),
            latestScore
        ];
        
        const labels = ['Jan', 'Mar', 'Jun', 'Sep', 'Today'];

        trendChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Risk Score (%)',
                    data: historicalScores,
                    borderColor: '#2563EB',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: '#fff',
                    pointBorderColor: '#2563EB',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { borderDash: [5, 5], color: '#e2e8f0' }
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#0f172a',
                        padding: 10,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return `Score: ${context.parsed.y}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    function renderComprehensiveResults(results) {
        document.getElementById('results-dashboard').classList.remove('hidden');
        
        const diseases = ['diabetes', 'heart', 'kidney', 'liver'];
        let allFactors = [];
        let allRecs = [];

        diseases.forEach(d => {
            const data = results[d];
            
            // Update Gauge Texts
            document.getElementById(`score-${d}`).textContent = `${data.risk_score}%`;
            const badge = document.getElementById(`badge-${d}`);
            badge.textContent = `${data.risk_category} RISK`;
            
            let color = '#22c55e'; // green
            let tailwindText = 'text-green-500';
            if (data.risk_category === 'Moderate') {
                color = '#f59e0b'; // amber
                tailwindText = 'text-amber-500';
            } else if (data.risk_category === 'High') {
                color = '#ef4444'; // red
                tailwindText = 'text-red-500';
            }
            
            badge.className = `mt-4 text-[10px] font-bold uppercase tracking-widest px-3 py-1 rounded-full bg-slate-50 border border-slate-200 ${tailwindText}`;

            // Draw Gauge
            const ctx = document.getElementById(`gauge-${d}`).getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    datasets: [{
                        data: [data.risk_score, 100 - data.risk_score],
                        backgroundColor: [color, '#f1f5f9'],
                        borderWidth: 0,
                        circumference: 180,
                        rotation: 270,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '80%',
                    plugins: { tooltip: { enabled: false }, legend: { display: false } },
                    animation: { animateRotate: true, animateScale: false }
                }
            });

            // Aggregate factors and recs
            if (data.factors) allFactors.push(...data.factors);
            if (data.recommendations) allRecs.push(...data.recommendations);
        });

        // Deduplicate
        allFactors = [...new Set(allFactors)];
        allRecs = [...new Set(allRecs)];

        const fList = document.getElementById('comprehensive-factors');
        fList.innerHTML = '';
        if (allFactors.length === 0) {
            fList.innerHTML = '<li class="text-sm text-slate-500">No major clinical risk factors detected.</li>';
        } else {
            allFactors.forEach(f => {
                fList.insertAdjacentHTML('beforeend', `<li class="text-sm text-slate-700 flex items-start gap-2"><i class="fa-solid fa-angle-right text-slate-400 mt-1"></i> ${f}</li>`);
            });
        }

        const rList = document.getElementById('comprehensive-recs');
        rList.innerHTML = '';
        allRecs.forEach(r => {
            rList.insertAdjacentHTML('beforeend', `<li class="text-sm text-slate-700 flex items-start gap-2"><i class="fa-solid fa-circle-check text-purple-500 mt-1"></i> ${r}</li>`);
        });

        document.getElementById('results-dashboard').scrollIntoView({ behavior: 'smooth' });
    }
});

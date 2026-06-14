document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadingState = document.getElementById('uploading-state');
    const dashboard = document.getElementById('report-dashboard');
    const btnNewUpload = document.getElementById('btn-new-upload');
    
    // Result elements
    const summaryText = document.getElementById('summary-text');
    const recsList = document.getElementById('recommendations-list');
    const abnormalContainer = document.getElementById('abnormal-values-container');

    // Handle drag events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('bg-blue-50', 'border-primary'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('bg-blue-50', 'border-primary'), false);
    });

    // Handle Drop
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) handleFiles(files);
    });

    // Handle Click Input
    fileInput.addEventListener('change', function() {
        if (this.files.length) handleFiles(this.files);
    });

    btnNewUpload.addEventListener('click', () => {
        dashboard.classList.add('hidden');
        dropZone.classList.remove('hidden');
        fileInput.value = ''; // clear
    });

    async function handleFiles(files) {
        const file = files[0];
        // Basic validation
        const validTypes = ['application/pdf', 'image/jpeg', 'image/png'];
        if (!validTypes.includes(file.type)) {
            alert("Invalid file type. Only PDF, JPG, and PNG are supported.");
            return;
        }
        
        // Show loading state
        dropZone.classList.add('hidden');
        uploadingState.classList.remove('hidden');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload-report', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                renderAnalysis(data.analysis);
            } else {
                throw new Error(data.error || 'Failed to analyze report.');
            }
        } catch (err) {
            alert('Error: ' + err.message);
            dropZone.classList.remove('hidden');
        } finally {
            uploadingState.classList.add('hidden');
        }
    }

    function renderAnalysis(analysis) {
        // Summary
        summaryText.textContent = analysis.summary || "No summary provided.";

        // Recommendations
        recsList.innerHTML = '';
        if (analysis.recommendations && analysis.recommendations.length > 0) {
            analysis.recommendations.forEach(r => {
                recsList.insertAdjacentHTML('beforeend', `<li class="text-sm text-slate-700 flex items-start gap-3"><i class="fa-solid fa-check text-secondary mt-1"></i> <span>${r}</span></li>`);
            });
        } else {
            recsList.innerHTML = '<li class="text-sm text-slate-500">No specific recommendations.</li>';
        }

        // Abnormal Values
        abnormalContainer.innerHTML = '';
        if (analysis.abnormal_values && analysis.abnormal_values.length > 0) {
            analysis.abnormal_values.forEach(item => {
                const badgeColor = item.status.toLowerCase().includes('high') ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700';
                const html = `
                    <div class="p-4 bg-slate-50 rounded-xl border border-slate-200">
                        <div class="flex justify-between items-start mb-2">
                            <span class="font-bold text-slate-800 text-sm">${item.metric}</span>
                            <span class="px-2 py-1 text-xs font-bold rounded ${badgeColor}">${item.status}</span>
                        </div>
                        <div class="flex justify-between text-xs text-slate-500">
                            <span>Value: <strong class="text-slate-800">${item.value}</strong></span>
                            <span>Range: ${item.range}</span>
                        </div>
                    </div>
                `;
                abnormalContainer.insertAdjacentHTML('beforeend', html);
            });
        } else {
            abnormalContainer.innerHTML = '<div class="text-sm text-slate-500 italic p-4 text-center">No abnormal values detected!</div>';
        }

        dashboard.classList.remove('hidden');
    }
});

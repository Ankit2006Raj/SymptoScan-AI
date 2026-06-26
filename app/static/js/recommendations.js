document.addEventListener('DOMContentLoaded', () => {
    // --- Daily Checklist Logic ---
    const checkboxes = document.querySelectorAll('.checklist-checkbox');
    const progressBar = document.getElementById('checklist-progress-bar');
    const progressText = document.getElementById('checklist-progress-text');
    
    // Load state from localStorage
    const savedChecklist = JSON.parse(localStorage.getItem('symptoscan_checklist') || '{}');
    
    // Function to update progress
    const updateChecklistProgress = () => {
        let checkedCount = 0;
        checkboxes.forEach(cb => {
            const span = cb.nextElementSibling;
            if (cb.checked) {
                checkedCount++;
                span.classList.add('line-through', 'opacity-60');
            } else {
                span.classList.remove('line-through', 'opacity-60');
            }
        });
        
        const percentage = Math.round((checkedCount / checkboxes.length) * 100);
        progressBar.style.width = percentage + '%';
        progressText.textContent = percentage + '%';
    };

    // Initialize checkboxes from saved state
    checkboxes.forEach(cb => {
        const taskId = cb.getAttribute('data-id');
        if (savedChecklist[taskId]) {
            cb.checked = true;
        }
        
        // Add event listener
        cb.addEventListener('change', (e) => {
            // Save state
            savedChecklist[taskId] = e.target.checked;
            localStorage.setItem('symptoscan_checklist', JSON.stringify(savedChecklist));
            updateChecklistProgress();
        });
    });
    
    // Initial render
    updateChecklistProgress();


    // --- Hydration Tracker Logic ---
    const maxHydration = 2.5; // L
    const glassVolume = 0.5; // L per glass
    const totalGlasses = Math.ceil(maxHydration / glassVolume);
    
    let currentGlasses = parseInt(localStorage.getItem('symptoscan_hydration') || '0', 10);
    
    const hydrationCurrentText = document.getElementById('hydration-current');
    const hydrationGlassesContainer = document.getElementById('hydration-glasses');
    
    const renderHydration = () => {
        // Update text
        const currentLiters = (currentGlasses * glassVolume).toFixed(1);
        hydrationCurrentText.textContent = currentLiters;
        
        // Render glasses
        hydrationGlassesContainer.innerHTML = '';
        for (let i = 0; i < totalGlasses; i++) {
            const glassDiv = document.createElement('div');
            
            if (i < currentGlasses) {
                // Filled glass
                glassDiv.className = 'w-1/5 h-10 bg-white text-blue-500 rounded-lg flex items-center justify-center text-xs font-bold cursor-pointer hover:bg-blue-50 transition';
                glassDiv.innerHTML = '<i class="fa-solid fa-glass-water"></i>';
                glassDiv.onclick = () => setHydration(i); // Clicking a filled glass reduces to that level
            } else if (i === currentGlasses) {
                // Next to fill
                glassDiv.className = 'w-1/5 h-10 bg-white/30 rounded-lg flex items-center justify-center text-xs font-bold cursor-pointer hover:bg-white/40 transition text-white';
                glassDiv.innerHTML = '<i class="fa-solid fa-plus"></i>';
                glassDiv.onclick = () => setHydration(i + 1);
            } else {
                // Empty glass
                glassDiv.className = 'w-1/5 h-10 bg-white/20 rounded-lg cursor-pointer hover:bg-white/30 transition';
                glassDiv.onclick = () => setHydration(i + 1);
            }
            
            hydrationGlassesContainer.appendChild(glassDiv);
        }
    };
    
    const setHydration = (amount) => {
        currentGlasses = amount;
        localStorage.setItem('symptoscan_hydration', currentGlasses);
        renderHydration();
    };
    
    // Initial render
    renderHydration();
});

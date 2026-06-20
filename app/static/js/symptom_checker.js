document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const steps = document.querySelectorAll('.step-content');
    const stepIndicators = document.querySelectorAll('.step-indicator');
    const progressBar = document.getElementById('progress-bar');

    // Buttons
    const btnNext1 = document.getElementById('btn-next-1');
    const btnBack2 = document.getElementById('btn-back-2');
    const btnAnalyze = document.getElementById('btn-analyze');
    const btnRestart = document.getElementById('btn-restart');

    // Inputs
    const ageInput = document.getElementById('age');
    const genderInput = document.getElementById('gender');
    const medicalHistoryInput = document.getElementById('medical-history');
    const symptomsInput = document.getElementById('symptoms');
    const durationInput = document.getElementById('duration');
    const severityInput = document.getElementById('severity');
    const severityValue = document.getElementById('severity-value');

    // Advanced Explorer UI Elements
    const tabCategories = document.getElementById('tab-categories');
    const tabBodyMap = document.getElementById('tab-bodymap');
    const viewCategories = document.getElementById('view-categories');
    const viewBodyMap = document.getElementById('view-bodymap');
    const currentCategoryTitle = document.getElementById('current-category-title');
    const symptomSearch = document.getElementById('symptom-search');
    const symptomList = document.getElementById('symptom-list');
    const selectedSymptomsContainer = document.getElementById('selected-symptoms-container');
    const selectedChips = document.getElementById('selected-chips');
    const selectedCount = document.getElementById('selected-count');
    const clearAllBtn = document.getElementById('clear-all-symptoms');
    const smartSuggestions = document.getElementById('smart-suggestions');
    const suggestionChips = document.getElementById('suggestion-chips');
    const bodyRegions = document.querySelectorAll('.body-region');

    // Result Elements
    const riskBadge = document.getElementById('risk-badge');
    const conditionsContainer = document.getElementById('conditions-container');
    const explanationText = document.getElementById('explanation-text');
    const recommendationsList = document.getElementById('recommendations-list');

    // --- State ---
    let currentStep = 1;
    let formData = {};

    // --- Severity Slider Update ---
    severityInput.addEventListener('input', (e) => {
        severityValue.textContent = e.target.value;

        // Change color based on severity
        const val = parseInt(e.target.value);
        if (val <= 3) {
            severityValue.className = 'text-green-500 font-bold';
        } else if (val <= 7) {
            severityValue.className = 'text-amber-500 font-bold';
        } else {
            severityValue.className = 'text-red-500 font-bold';
        }
    });


    // --- Step 1 Premium UI Logic ---
    const genderRadios = document.querySelectorAll('input[name="gender-select"]');
    genderRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            const genderInput = document.getElementById('gender');
            if (genderInput) genderInput.value = e.target.value;
        });
    });

    const btnAgeMinus = document.getElementById('age-minus');
    const btnAgePlus = document.getElementById('age-plus');
    const ageInputElem = document.getElementById('age');
    if (btnAgeMinus && btnAgePlus && ageInputElem) {
        btnAgeMinus.addEventListener('click', () => {
            let val = parseInt(ageInputElem.value) || 30;
            if (val > 1) ageInputElem.value = val - 1;
        });
        btnAgePlus.addEventListener('click', () => {
            let val = parseInt(ageInputElem.value) || 30;
            if (val < 120) ageInputElem.value = val + 1;
        });
    }

    const historyChips = document.querySelectorAll('.history-chip');
    historyChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const val = chip.dataset.condition;
            const historyInput = document.getElementById('medical-history');
            const current = historyInput.value.trim();
            if (val === 'None') {
                historyInput.value = 'None';
            } else {
                if (current.toLowerCase() === 'none') {
                    historyInput.value = val;
                } else {
                    if (!current.includes(val)) {
                        historyInput.value = current ? current + ', ' + val : val;
                    }
                }
            }
        });
    });

    // --- Navigation Functions ---
    const goToStep = (stepNumber) => {
        // Hide all
        steps.forEach(step => {
            step.classList.remove('active');
            step.classList.add('hidden');
        });

        // Show target
        const targetStep = document.getElementById(`step-${stepNumber}`);
        targetStep.classList.remove('hidden');
        setTimeout(() => targetStep.classList.add('active'), 50);

        // Update Indicators
        stepIndicators.forEach((indicator, index) => {
            const circle = indicator.querySelector('.step-circle');
            const text = indicator.querySelector('.step-text');

            if (index + 1 < stepNumber) {
                circle.className = 'w-10 h-10 rounded-full bg-secondary text-white flex items-center justify-center font-bold shadow-md transition-colors duration-300 step-circle';
                circle.innerHTML = '<i class="fa-solid fa-check"></i>';
                text.className = 'text-xs font-semibold mt-2 text-secondary step-text';
            } else if (index + 1 === stepNumber) {
                circle.className = 'w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-bold shadow-md transition-colors duration-300 step-circle';
                circle.innerHTML = `${index + 1}`;
                text.className = 'text-xs font-semibold mt-2 text-primary step-text';
            } else {
                circle.className = 'w-10 h-10 rounded-full bg-white border-2 border-slate-200 text-slate-400 flex items-center justify-center font-bold shadow-sm transition-colors duration-300 step-circle';
                circle.innerHTML = `${index + 1}`;
                text.className = 'text-xs font-semibold mt-2 text-slate-400 step-text';
            }
        });

        const progressPercentages = { 1: '25%', 2: '50%', 3: '75%', 4: '100%' };
        progressBar.style.width = progressPercentages[stepNumber];
        currentStep = stepNumber;
        
        // Scroll to top of the page smoothly
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // --- Advanced Explorer Logic ---
    let selectedSymptomsSet = new Set();
    let currentCategory = "General Symptoms";

    const symptomDictionary = {
        "Head & Neurological": [
            { name: "Headache", icon: "fa-head-side-virus", desc: "Pain or discomfort in the head, scalp, or neck." },
            { name: "Dizziness", icon: "fa-arrows-spin", desc: "Feeling faint, woozy, weak or unsteady." },
            { name: "Confusion", icon: "fa-question", desc: "Inability to think as clearly or quickly as normal." },
            { name: "Vision Changes", icon: "fa-eye", desc: "Blurriness, double vision, or loss of vision." },
            { name: "Numbness", icon: "fa-hand-dots", desc: "Loss of sensation in any part of the body." },
            { name: "Seizures", icon: "fa-bolt", desc: "Sudden, uncontrolled electrical disturbance in the brain." },
            { name: "Memory Loss", icon: "fa-brain", desc: "Unusual forgetfulness or inability to recall past events." }
        ],
        "Respiratory": [
            { name: "Cough", icon: "fa-lungs-virus", desc: "Sudden, forceful hacking sound to clear airways." },
            { name: "Shortness of breath", icon: "fa-lungs", desc: "Intense tightening in the chest, air hunger." },
            { name: "Wheezing", icon: "fa-wind", desc: "High-pitched whistling sound made while breathing." },
            { name: "Sputum Production", icon: "fa-droplet", desc: "Coughing up thick mucus." }
        ],
        "Cardiovascular": [
            { name: "Chest pain", icon: "fa-heart-pulse", desc: "Discomfort or pain anywhere in the front of your body between your neck and upper abdomen." },
            { name: "Palpitations", icon: "fa-heartbeat", desc: "Feelings of having a fast-beating, fluttering or pounding heart." },
            { name: "Swelling in Legs", icon: "fa-shoe-prints", desc: "Edema or fluid buildup in the lower extremities." }
        ],
        "Digestive": [
            { name: "Nausea", icon: "fa-face-nauseated", desc: "Stomach discomfort and the sensation of wanting to vomit." },
            { name: "Vomiting", icon: "fa-bowl-food", desc: "Forceful emptying of the stomach." },
            { name: "Diarrhea", icon: "fa-poop", desc: "Loose, watery and possibly more frequent bowel movements." },
            { name: "Abdominal Pain", icon: "fa-stomach", desc: "Pain that you feel anywhere between your chest and groin." },
            { name: "Heartburn", icon: "fa-fire", desc: "A burning pain in your chest, just behind your breastbone." }
        ],
        "Musculoskeletal": [
            { name: "Joint Pain", icon: "fa-bone", desc: "Discomfort, pain or inflammation arising from any part of a joint." },
            { name: "Muscle Ache", icon: "fa-dumbbell", desc: "Pain, tenderness, or weakness in the muscles." },
            { name: "Back Pain", icon: "fa-person", desc: "Physical discomfort occurring anywhere on the spine or back." },
            { name: "Stiffness", icon: "fa-person-cane", desc: "Difficulty moving joints or muscles." }
        ],
        "Skin": [
            { name: "Rash", icon: "fa-allergies", desc: "Noticeable change in the texture or color of your skin." },
            { name: "Itching", icon: "fa-hand-pointer", desc: "An irritating sensation that makes you want to scratch." },
            { name: "Redness", icon: "fa-droplet", desc: "Erythema or redness of the skin." }
        ],
        "Mental Health": [
            { name: "Anxiety", icon: "fa-brain", desc: "Intense, excessive, and persistent worry and fear." },
            { name: "Depression", icon: "fa-cloud-rain", desc: "Persistent feeling of sadness and loss of interest." },
            { name: "Insomnia", icon: "fa-bed", desc: "Difficulty falling asleep or staying asleep." },
            { name: "Mood Swings", icon: "fa-masks-theater", desc: "Rapid or extreme changes in mood." }
        ],
        "General Symptoms": [
            { name: "Fever", icon: "fa-thermometer-half", desc: "A temporary increase in your body temperature." },
            { name: "Fatigue", icon: "fa-battery-quarter", desc: "Unrelenting exhaustion." },
            { name: "Chills", icon: "fa-snowflake", desc: "Feeling cold with shivering." },
            { name: "Sweating", icon: "fa-droplet", desc: "Excessive perspiration." },
            { name: "Weight Loss", icon: "fa-weight-scale", desc: "Unexplained drop in body weight." },
            { name: "Weakness", icon: "fa-person-falling", desc: "Lack of physical or muscle strength." }
        ],
        "Women's Health": [
            { name: "Pelvic Pain", icon: "fa-person-dress", desc: "Pain in the lowest part of your abdomen and pelvis." },
            { name: "Irregular Periods", icon: "fa-calendar-xmark", desc: "Menstrual cycles that are longer or shorter than normal." },
            { name: "Hot Flashes", icon: "fa-fire", desc: "Sudden feelings of warmth." }
        ],
        "Emergency Symptoms": [
            { name: "Severe Chest Pain", icon: "fa-heart-crack", desc: "Crushing chest pain radiating to arm or jaw." },
            { name: "Difficulty Breathing", icon: "fa-lungs-virus", desc: "Gasping for air or severe shortness of breath." },
            { name: "Sudden Numbness", icon: "fa-user-injured", desc: "Sudden numbness or weakness in the face, arm, or leg." },
            { name: "Loss of Consciousness", icon: "fa-bed-pulse", desc: "Fainting or unresponsiveness." }
        ]
    };

    const suggestionsRules = {
        "Fever": ["Chills", "Fatigue", "Muscle Ache", "Headache"],
        "Cough": ["Shortness of breath", "Sore Throat", "Fever"],
        "Nausea": ["Vomiting", "Diarrhea", "Abdominal Pain"],
        "Headache": ["Nausea", "Vision Changes", "Dizziness"]
    };

    const initExplorer = () => {
        renderCategoryMenu();
        loadCategory(currentCategory);
        updateSelectedUI();
    };

    const renderCategoryMenu = () => {
        viewCategories.innerHTML = '';
        Object.keys(symptomDictionary).forEach(cat => {
            const isEmergency = cat === 'Emergency Symptoms';
            const isActive = cat === currentCategory;

            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = `w-full text-left px-4 py-3 rounded-xl transition-all font-semibold text-sm mb-1 ${isActive
                    ? 'bg-white shadow-sm border border-primary/20 text-primary'
                    : (isEmergency ? 'text-red-600 hover:bg-red-50' : 'text-slate-600 hover:bg-white hover:shadow-sm')
                }`;

            let icon = 'fa-folder';
            if (cat === 'Head & Neurological') icon = 'fa-brain';
            if (cat === 'Respiratory') icon = 'fa-lungs';
            if (cat === 'Cardiovascular') icon = 'fa-heart';
            if (cat === 'Digestive') icon = 'fa-stomach';
            if (cat === 'Musculoskeletal') icon = 'fa-bone';
            if (cat === 'Skin') icon = 'fa-allergies';
            if (cat === 'Mental Health') icon = 'fa-masks-theater';
            if (cat === 'General Symptoms') icon = 'fa-list';
            if (cat === 'Women\'s Health') icon = 'fa-person-dress';
            if (isEmergency) icon = 'fa-triangle-exclamation';

            btn.innerHTML = `<i class="fa-solid ${icon} w-6 text-center ${isEmergency ? 'text-red-500' : (isActive ? 'text-primary' : 'text-slate-400')}"></i> ${cat}`;

            btn.addEventListener('click', () => {
                currentCategory = cat;
                renderCategoryMenu();
                loadCategory(cat);
            });
            viewCategories.appendChild(btn);
        });
    };

    const loadCategory = (cat, filter = '') => {
        currentCategoryTitle.innerHTML = `<i class="fa-solid fa-layer-group text-primary"></i> ${cat}`;
        symptomList.innerHTML = '';

        let symptoms = symptomDictionary[cat] || [];
        if (filter) {
            symptoms = symptoms.filter(s => s.name.toLowerCase().includes(filter.toLowerCase()) || s.desc.toLowerCase().includes(filter.toLowerCase()));
        }

        if (symptoms.length === 0) {
            symptomList.innerHTML = '<div class="text-center py-8 text-slate-400 text-sm"><i class="fa-solid fa-search mb-2 text-2xl"></i><br>No symptoms found.</div>';
            return;
        }

        symptoms.forEach(s => {
            const isSelected = selectedSymptomsSet.has(s.name);
            const card = document.createElement('div');
            card.className = `p-3 rounded-xl border transition-all cursor-pointer flex items-center gap-3 ${isSelected
                    ? 'bg-blue-50/80 border-blue-200 shadow-sm'
                    : 'bg-white border-slate-100 shadow-sm hover:border-primary/30 hover:shadow-md'
                }`;

            card.innerHTML = `
                <div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${isSelected ? 'bg-primary text-white' : 'bg-slate-50 text-slate-400'}">
                    <i class="fa-solid ${s.icon}"></i>
                </div>
                <div class="flex-1">
                    <h5 class="font-bold text-sm ${isSelected ? 'text-blue-800' : 'text-slate-800'}">${s.name}</h5>
                    <p class="text-xs text-slate-500 line-clamp-1">${s.desc}</p>
                </div>
                <div class="flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors ${isSelected ? 'bg-primary border-primary text-white' : 'border-slate-200 text-transparent'
                }">
                    <i class="fa-solid fa-check text-xs"></i>
                </div>
            `;

            card.addEventListener('click', () => {
                if (isSelected) {
                    selectedSymptomsSet.delete(s.name);
                } else {
                    selectedSymptomsSet.add(s.name);
                }
                loadCategory(cat, symptomSearch.value);
                updateSelectedUI();
                generateSmartSuggestions();
            });

            symptomList.appendChild(card);
        });
    };

    const updateSelectedUI = () => {
        selectedCount.textContent = selectedSymptomsSet.size;
        selectedChips.innerHTML = '';

        if (selectedSymptomsSet.size > 0) {
            selectedSymptomsContainer.classList.remove('hidden');
            selectedSymptomsSet.forEach(s => {
                const chip = document.createElement('span');
                chip.className = 'inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-white text-blue-700 border border-blue-200 shadow-sm';
                chip.innerHTML = `${s} <button type="button" class="ml-2 text-blue-400 hover:text-red-500 transition focus:outline-none"><i class="fa-solid fa-xmark"></i></button>`;

                chip.querySelector('button').addEventListener('click', () => {
                    selectedSymptomsSet.delete(s);
                    loadCategory(currentCategory, symptomSearch.value);
                    updateSelectedUI();
                    generateSmartSuggestions();
                });

                selectedChips.appendChild(chip);
            });
        } else {
            selectedSymptomsContainer.classList.add('hidden');
        }
    };

    const generateSmartSuggestions = () => {
        suggestionChips.innerHTML = '';
        let suggested = new Set();

        selectedSymptomsSet.forEach(s => {
            if (suggestionsRules[s]) {
                suggestionsRules[s].forEach(rec => {
                    if (!selectedSymptomsSet.has(rec)) {
                        suggested.add(rec);
                    }
                });
            }
        });

        if (suggested.size > 0) {
            smartSuggestions.classList.remove('hidden');
            suggested.forEach(s => {
                const chip = document.createElement('button');
                chip.type = 'button';
                chip.className = 'inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-white text-emerald-700 border border-emerald-200 shadow-sm hover:bg-emerald-50 transition';
                chip.innerHTML = `<i class="fa-solid fa-plus mr-1"></i> ${s}`;

                chip.addEventListener('click', () => {
                    selectedSymptomsSet.add(s);
                    loadCategory(currentCategory, symptomSearch.value);
                    updateSelectedUI();
                    generateSmartSuggestions();
                });

                suggestionChips.appendChild(chip);
            });
        } else {
            smartSuggestions.classList.add('hidden');
        }
    };

    // --- Advanced Explorer Event Listeners ---
    tabCategories.addEventListener('click', () => {
        tabCategories.className = 'flex-1 py-2 text-sm font-bold bg-primary/10 text-primary rounded-lg transition-colors';
        tabBodyMap.className = 'flex-1 py-2 text-sm font-bold text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors ml-2';
        viewCategories.classList.remove('hidden');
        viewBodyMap.classList.add('hidden');
    });

    tabBodyMap.addEventListener('click', () => {
        tabBodyMap.className = 'flex-1 py-2 text-sm font-bold bg-primary/10 text-primary rounded-lg transition-colors ml-2';
        tabCategories.className = 'flex-1 py-2 text-sm font-bold text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors';
        viewBodyMap.classList.remove('hidden');
        viewCategories.classList.add('hidden');
    });

    bodyRegions.forEach(region => {
        region.addEventListener('click', () => {
            const cat = region.dataset.region;
            currentCategory = cat;
            tabCategories.click();
            renderCategoryMenu();
            loadCategory(cat);
            document.getElementById('view-categories').scrollTop = 0;
        });
    });

    symptomSearch.addEventListener('input', (e) => {
        const val = e.target.value;
        if (val && val.length > 2) {
            currentCategoryTitle.innerHTML = `<i class="fa-solid fa-search text-primary"></i> Search Results`;
            symptomList.innerHTML = '';
            let foundAny = false;

            Object.keys(symptomDictionary).forEach(cat => {
                const matched = symptomDictionary[cat].filter(s => s.name.toLowerCase().includes(val.toLowerCase()) || s.desc.toLowerCase().includes(val.toLowerCase()));
                if (matched.length > 0) {
                    foundAny = true;
                    const header = document.createElement('div');
                    header.className = 'text-xs font-bold text-slate-400 uppercase tracking-wider mt-2 mb-1 px-1';
                    header.textContent = cat;
                    symptomList.appendChild(header);

                    matched.forEach(s => {
                        const isSelected = selectedSymptomsSet.has(s.name);
                        const card = document.createElement('div');
                        card.className = `p-3 rounded-xl border transition-all cursor-pointer flex items-center gap-3 mb-2 ${isSelected ? 'bg-blue-50/80 border-blue-200' : 'bg-white border-slate-100 hover:border-primary/30 hover:shadow-md'
                            }`;
                        card.innerHTML = `
                            <div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${isSelected ? 'bg-primary text-white' : 'bg-slate-50 text-slate-400'}">
                                <i class="fa-solid ${s.icon}"></i>
                            </div>
                            <div class="flex-1">
                                <h5 class="font-bold text-sm ${isSelected ? 'text-blue-800' : 'text-slate-800'}">${s.name}</h5>
                                <p class="text-xs text-slate-500 line-clamp-1">${s.desc}</p>
                            </div>
                            <div class="flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors ${isSelected ? 'bg-primary border-primary text-white' : 'border-slate-200 text-transparent'
                            }">
                                <i class="fa-solid fa-check text-xs"></i>
                            </div>
                        `;
                        card.addEventListener('click', () => {
                            if (isSelected) {
                                selectedSymptomsSet.delete(s.name);
                            } else {
                                selectedSymptomsSet.add(s.name);
                            }
                            updateSelectedUI();
                            generateSmartSuggestions();
                            symptomSearch.dispatchEvent(new Event('input'));
                        });
                        symptomList.appendChild(card);
                    });
                }
            });

            if (!foundAny) {
                symptomList.innerHTML = '<div class="text-center py-8 text-slate-400 text-sm"><i class="fa-solid fa-search mb-2 text-2xl"></i><br>No symptoms found.</div>';
            }
        } else {
            loadCategory(currentCategory);
        }
    });

    clearAllBtn.addEventListener('click', () => {
        selectedSymptomsSet.clear();
        loadCategory(currentCategory, symptomSearch.value);
        updateSelectedUI();
        smartSuggestions.classList.add('hidden');
    });

    initExplorer();

    // --- Form Event Listeners ---
    btnNext1.addEventListener('click', () => {
        // Validate
        if (!ageInput.value || !genderInput.value) {
            alert('Please fill in your age and gender.');
            return;
        }

        // Save data
        formData.age = parseInt(ageInput.value);
        formData.gender = genderInput.value;
        formData.medical_history = medicalHistoryInput.value;

        goToStep(2);
    });

    btnBack2.addEventListener('click', () => {
        goToStep(1);
    });

    btnAnalyze.addEventListener('click', async () => {
        // Merge structured symptoms with free text
        let combinedSymptoms = Array.from(selectedSymptomsSet).join(', ');
        if (symptomsInput.value.trim() !== '') {
            combinedSymptoms += (combinedSymptoms ? '. Additional details: ' : '') + symptomsInput.value.trim();
        }

        // Validate
        if (!combinedSymptoms || !durationInput.value) {
            alert('Please select or describe your symptoms and select a duration.');
            return;
        }

        // Save data
        formData.symptoms = combinedSymptoms;
        formData.duration = durationInput.value;
        formData.severity = parseInt(severityInput.value);

        // Go to Loading Step
        goToStep(3);
        simulateLoadingProgress();

        // Make API Call
        try {
            const response = await fetch('/api/analyze-symptoms', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.success) {
                // Clear any previous errors
                const existingBanner = document.getElementById('api-error-banner');
                if (existingBanner) existingBanner.remove();

                renderResults(data.results, data.assessment_id);
                setTimeout(() => goToStep(4), 500); // Small delay to let loading finish visually
            } else {
                const errorMessage = data.details ? `${data.error} - ${data.details}` : (data.error || 'Failed to analyze symptoms');
                throw new Error(errorMessage);
            }
        } catch (error) {
            goToStep(2); // Go back to input on error

            // Create or update graceful error banner
            let errorBanner = document.getElementById('api-error-banner');
            if (!errorBanner) {
                errorBanner = document.createElement('div');
                errorBanner.id = 'api-error-banner';
                errorBanner.className = 'bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded-r-lg shadow-sm transition-all animate-fade-in-up';

                // Try to find the step-2 container
                const step2Content = document.querySelector('#step-2 > div.bg-white') || document.getElementById('step-2');
                if (step2Content) {
                    step2Content.insertBefore(errorBanner, step2Content.firstChild);
                }
            }

            errorBanner.innerHTML = `
                <div class="flex items-start">
                    <div class="flex-shrink-0 mt-0.5">
                        <i class="fa-solid fa-circle-exclamation text-red-500 text-lg"></i>
                    </div>
                    <div class="ml-3">
                        <h3 class="text-sm font-bold text-red-800">Analysis Failed</h3>
                        <div class="mt-1 text-sm text-red-700">
                            <p>${error.message}</p>
                        </div>
                    </div>
                </div>
            `;

            errorBanner.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    });

    btnRestart.addEventListener('click', () => {
        // Reset form
        document.getElementById('form-step-1').reset();
        document.getElementById('form-step-2').reset();
        severityValue.textContent = '5';
        severityValue.className = 'text-primary font-bold';

        // Reset advanced UI
        selectedSymptomsSet.clear();
        currentCategory = "General Symptoms";
        symptomSearch.value = "";
        initExplorer();

        formData = {};
        goToStep(1);
    });

    // --- Helper Functions ---
    const simulateLoadingProgress = () => {
        const bar = document.getElementById('ai-progress-bar');
        const text = document.getElementById('loading-text');
        const pctText = document.getElementById('ai-progress-percentage');

        const messages = [
            "Initializing diagnostic algorithms...",
            "Cross-referencing medical database...",
            "Calculating probability scores...",
            "Generating personalized action plan..."
        ];

        let progress = 0;
        let messageIndex = 0;

        bar.style.width = '0%';
        if (pctText) pctText.textContent = '0%';

        const interval = setInterval(() => {
            progress += Math.random() * 12;
            if (progress >= 95) {
                clearInterval(interval);
                progress = 95; // Hold at 95% until API returns
            }

            bar.style.width = `${progress}%`;
            if (pctText) pctText.textContent = `${Math.round(progress)}%`;

            if (progress > 25 && messageIndex === 0) { messageIndex++; text.textContent = messages[messageIndex]; }
            if (progress > 50 && messageIndex === 1) { messageIndex++; text.textContent = messages[messageIndex]; }
            if (progress > 75 && messageIndex === 2) { messageIndex++; text.textContent = messages[messageIndex]; }

        }, 300);
    };

    const renderResults = (results, assessment_id) => {
        // --- 1. Populate Symptom Summary ---
        document.getElementById('summary-symptoms').textContent = formData.symptoms || 'None selected';
        document.getElementById('summary-duration').textContent = formData.duration || 'N/A';
        document.getElementById('summary-severity').textContent = formData.severity || '5';
        document.getElementById('summary-history').textContent = formData.medical_history || 'None reported';

        // --- 2. Calculate Risk Score and Render Badge ---
        const riskBadge = document.getElementById('risk-badge');
        const emergencyBanner = document.getElementById('emergency-banner');
        const risk = results.risk_level.toLowerCase();
        
        let baseScore = 0;
        let maxConf = 0;
        if (results.conditions && results.conditions.length > 0) {
            maxConf = results.conditions[0].confidence_score || results.conditions[0].match_percentage || 0;
        }

        if (risk === 'low') {
            riskBadge.className = 'inline-flex items-center px-4 py-1.5 rounded-full text-xs font-bold mb-4 uppercase tracking-widest bg-emerald-500/20 text-emerald-100 border border-emerald-400/30 backdrop-blur-md shadow-sm';
            riskBadge.innerHTML = '<i class="fa-solid fa-shield-check mr-2"></i> Low Risk';
            if (emergencyBanner) emergencyBanner.classList.add('hidden');
            baseScore = 20 + (maxConf * 0.2); // Maps to 20-40
        } else if (risk === 'high' || risk === 'severe') {
            riskBadge.className = 'inline-flex items-center px-4 py-1.5 rounded-full text-xs font-bold mb-4 uppercase tracking-widest bg-red-500/80 text-white border border-red-400/50 backdrop-blur-md shadow-sm animate-pulse';
            riskBadge.innerHTML = '<i class="fa-solid fa-triangle-exclamation mr-2"></i> High Risk';
            if (emergencyBanner) emergencyBanner.classList.remove('hidden');
            baseScore = 80 + (maxConf * 0.2); // Maps to 80-100
        } else {
            riskBadge.className = 'inline-flex items-center px-4 py-1.5 rounded-full text-xs font-bold mb-4 uppercase tracking-widest bg-amber-500/30 text-amber-100 border border-amber-400/40 backdrop-blur-md shadow-sm';
            riskBadge.innerHTML = '<i class="fa-solid fa-circle-exclamation mr-2"></i> Moderate Risk';
            if (emergencyBanner) emergencyBanner.classList.add('hidden');
            baseScore = 40 + (maxConf * 0.4); // Maps to 40-80
        }

        const finalScore = Math.min(100, Math.round(baseScore));
        
        // Animate Score Counter
        const scoreElem = document.getElementById('risk-score-value');
        let currentCount = 0;
        const duration = 1500;
        const stepTime = Math.abs(Math.floor(duration / finalScore)) || 10;
        const timer = setInterval(() => {
            currentCount += 1;
            scoreElem.textContent = currentCount;
            if (currentCount >= finalScore) {
                scoreElem.textContent = finalScore;
                clearInterval(timer);
            }
        }, stepTime);

        // Animate SVG Circle
        const circle = document.getElementById('risk-meter-circle');
        const circumference = 351.8; // 2 * pi * 56
        const offset = circumference - (finalScore / 100) * circumference;
        
        // Color transition based on score
        if (finalScore >= 80) circle.className = 'text-red-500 transition-all duration-1000 ease-out';
        else if (finalScore >= 40) circle.className = 'text-amber-400 transition-all duration-1000 ease-out';
        else circle.className = 'text-emerald-400 transition-all duration-1000 ease-out';
        
        setTimeout(() => {
            circle.style.strokeDashoffset = offset;
        }, 100);

        // --- 3. Render Conditions ---
        const conditionsContainer = document.getElementById('conditions-container');
        conditionsContainer.innerHTML = '';
        results.conditions.forEach(cond => {
            const width = cond.confidence_score || cond.match_percentage || 0;
            const barColor = width > 75 ? 'from-red-500 to-rose-400' : (width > 50 ? 'from-amber-500 to-orange-400' : 'from-blue-500 to-cyan-400');
            const bgHover = width > 75 ? 'hover:border-red-300' : 'hover:border-blue-300';

            const html = `
                <div class="bg-white rounded-xl p-4 border border-slate-100 shadow-sm transition-all ${bgHover} group">
                    <div class="flex justify-between items-center mb-3">
                        <h5 class="font-bold text-slate-800 text-sm group-hover:text-primary transition-colors">${cond.name}</h5>
                        <span class="text-xs font-bold text-slate-600 bg-slate-100 px-3 py-1 rounded-full">${width}% Match</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden shadow-inner">
                        <div class="h-2 rounded-full bg-gradient-to-r ${barColor} relative" style="width: ${width}%">
                            <div class="absolute inset-0 bg-white/20 animate-pulse"></div>
                        </div>
                    </div>
                </div>
            `;
            conditionsContainer.insertAdjacentHTML('beforeend', html);
        });

        // --- 4. Render Explanation ---
        const explanationText = document.getElementById('explanation-text');
        explanationText.textContent = results.explanation;

        // --- 5. Categorize & Render Recommendations ---
        const consultDoctorList = document.getElementById('consult-doctor-list');
        const homeCareList = document.getElementById('home-care-list');
        consultDoctorList.innerHTML = '';
        homeCareList.innerHTML = '';

        const consultKeywords = ['doctor', 'physician', 'hospital', 'emergency', 'medical attention', 'consult', 'evaluation', 'test', 'scan'];
        
        let hasConsult = false;
        let hasHomeCare = false;

        results.recommendations.forEach(rec => {
            const lowerRec = rec.toLowerCase();
            const isConsult = consultKeywords.some(kw => lowerRec.includes(kw));

            const html = `
                <li class="flex items-start gap-3">
                    <i class="fa-solid fa-circle-check mt-1 ${isConsult ? 'text-amber-500' : 'text-emerald-500'} text-xs"></i>
                    <span class="leading-snug">${rec}</span>
                </li>
            `;

            if (isConsult) {
                consultDoctorList.insertAdjacentHTML('beforeend', html);
                hasConsult = true;
            } else {
                homeCareList.insertAdjacentHTML('beforeend', html);
                hasHomeCare = true;
            }
        });

        if (!hasConsult) consultDoctorList.innerHTML = '<li class="text-slate-400 italic text-xs">No specific urgent medical consultations recommended.</li>';
        if (!hasHomeCare) homeCareList.innerHTML = '<li class="text-slate-400 italic text-xs">No specific home care or lifestyle changes specified.</li>';

        // --- 6. Render Red Flag Warnings ---
        const redFlagsContainer = document.getElementById('red-flags-container');
        const redFlagsList = document.getElementById('red-flags-list');
        redFlagsList.innerHTML = '';
        if (results.red_flag_warnings && results.red_flag_warnings.length > 0) {
            redFlagsContainer.classList.remove('hidden');
            results.red_flag_warnings.forEach(flag => {
                redFlagsList.insertAdjacentHTML('beforeend', `<li>${flag}</li>`);
            });
        } else {
            redFlagsContainer.classList.add('hidden');
        }

        // --- 7. Render Follow-Up Questions ---
        const followUpList = document.getElementById('follow-up-list');
        followUpList.innerHTML = '';
        if (results.follow_up_questions && results.follow_up_questions.length > 0) {
            results.follow_up_questions.forEach(q => {
                followUpList.insertAdjacentHTML('beforeend', `<li class="flex items-start gap-3"><i class="fa-solid fa-chevron-right text-primary mt-1 text-xs"></i> <span>${q}</span></li>`);
            });
        } else {
            followUpList.innerHTML = '<li class="text-slate-400 italic text-xs">No specific follow-up questions at this time.</li>';
        }

        // Setup Download and View Events
        const btnDownload = document.getElementById('btn-download');
        if (btnDownload) {
            const newBtn = btnDownload.cloneNode(true);
            btnDownload.parentNode.replaceChild(newBtn, btnDownload);

            newBtn.addEventListener('click', () => {
                if (assessment_id) {
                    window.location.href = `/api/export-report/assessment/${assessment_id}`;
                } else {
                    alert("Assessment ID not found. Cannot download report.");
                }
            });
        }
        
        const btnView = document.getElementById('btn-view');
        if (btnView) {
            const newBtnView = btnView.cloneNode(true);
            btnView.parentNode.replaceChild(newBtnView, btnView);

            newBtnView.addEventListener('click', () => {
                if (assessment_id) {
                    window.open(`/api/export-report/assessment/${assessment_id}?view=1`, '_blank');
                } else {
                    alert("Assessment ID not found. Cannot view report.");
                }
            });
        }
    };
});

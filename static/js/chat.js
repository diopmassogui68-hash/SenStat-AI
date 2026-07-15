/* 
 * SenStat AI - Logique Frontend Principale
 * Auteur: Serigne Mbacke Faye (Cœur JS) & Sanor Mangane (Bonus)
 */

let chartInstance = null;
let mapInstance = null;
let mapLayerGroup = null;
let chatHistoryData = []; // Bonus: Historique de session client

// Coordonnées approximatives des 14 capitales régionales
const regionCoords = {
    'Dakar': [14.6928, -17.4467],
    'Thiès': [14.7910, -16.9248],
    'Diourbel': [14.6533, -16.2300],
    'Kaolack': [14.1333, -16.2533],
    'Fatick': [14.3333, -16.4167],
    'Kaffrine': [14.1059, -15.5508],
    'Tambacounda': [13.7689, -13.6672],
    'Kédougou': [12.5528, -12.1803],
    'Kolda': [12.8833, -14.9500],
    'Sédhiou': [12.7081, -15.5569],
    'Ziguinchor': [12.5833, -16.2733],
    'Saint-Louis': [16.0306, -16.4817],
    'Louga': [15.6167, -16.2167],
    'Matam': [15.6559, -13.2533]
};

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('questionForm');
    const input = document.getElementById('questionInput');
    const sendBtn = document.getElementById('sendBtn');
    const historyContainer = document.getElementById('chatHistory');
    const loader = document.getElementById('loadingIndicator');
    const tableBody = document.getElementById('tableBody');
    const emptyChartMsg = document.getElementById('emptyChartMsg');
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const exportCsvBtn = document.getElementById('exportCsvBtn');
    const exportPdfBtn = document.getElementById('exportPdfBtn');
    
    // Nouveaux éléments Map/Chart toggle
    const btnShowChart = document.getElementById('btnShowChart');
    const btnShowMap = document.getElementById('btnShowMap');
    const chartContainer = document.getElementById('chartContainer');
    const mapContainer = document.getElementById('mapContainer');
    
    // Initialiser la carte Leaflet
    initMap();
    
    // Toggle Event Listeners
    btnShowChart.addEventListener('click', () => {
        btnShowChart.classList.add('active');
        btnShowMap.classList.remove('active');
        chartContainer.classList.remove('d-none');
        mapContainer.classList.add('d-none');
    });
    
    btnShowMap.addEventListener('click', () => {
        btnShowMap.classList.add('active');
        btnShowChart.classList.remove('active');
        mapContainer.classList.remove('d-none');
        chartContainer.classList.add('d-none');
        // Obligatoire pour Leaflet après un display: none
        setTimeout(() => mapInstance.invalidateSize(), 100);
    });
    
    // Initialisation du thème sombre (Bonus Sanor)
    const currentTheme = localStorage.getItem('theme') || 'light';
    setTheme(currentTheme);

    themeToggle.addEventListener('click', () => {
        const newTheme = document.documentElement.getAttribute('data-bs-theme') === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
    });

    function setTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        if(theme === 'dark') {
            themeIcon.classList.replace('bi-moon-fill', 'bi-sun-fill');
            themeIcon.classList.add('text-warning');
        } else {
            themeIcon.classList.replace('bi-sun-fill', 'bi-moon-fill');
            themeIcon.classList.remove('text-warning');
        }
    }

    // Gestion du formulaire
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const question = input.value.trim();
        if (!question) return;

        // Ajouter la question à l'historique UI
        appendMessage(question, 'user-msg', '<i class="bi bi-person me-2"></i>Vous');
        input.value = '';
        input.disabled = true;
        sendBtn.disabled = true;
        
        // Afficher le loader
        loader.classList.remove('d-none');
        
        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            
            const response = await fetch('/api/question/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ question: question })
            });

            const data = await response.json();
            
            if (response.ok) {
                // Succès : Afficher la réponse
                let msgHtml = `${data.answer}`;
                
                // Mettre en évidence l'utilisation de l'IA si activée
                if(data.metadata && data.metadata.ai_used) {
                    msgHtml += `
                        <div class="intent-details mt-2">
                            <span class="badge bg-primary"><i class="bi bi-stars"></i> Généré par IA Gemini</span>
                        </div>
                    `;
                }
                
                if(data.metadata && data.metadata.cached) {
                    msgHtml += `
                        <div class="intent-details mt-2">
                            <span class="badge bg-success"><i class="bi bi-lightning-charge"></i> Réponse servie depuis le Cache (Rapide)</span>
                        </div>
                    `;
                }

                appendMessage(msgHtml, 'bot-msg', '<i class="bi bi-robot me-2"></i>SenStat AI');
                speakText(msgHtml);
                
                // Mettre à jour le tableau
                updateTable(data.table);
                
                // Mettre à jour le graphique (Destruction propre)
                updateChart(data.chart);
                
                // Mettre à jour la carte Leaflet
                updateMap(data.table, data.metadata?.intent_debug?.indicator);
                
                // Activer l'export CSV et PDF si données
                if(data.table && data.table.length > 0) {
                    exportCsvBtn.classList.remove('d-none');
                    exportPdfBtn.classList.remove('d-none');
                    exportCsvBtn.onclick = () => exportToCsv(data.table);
                    exportPdfBtn.onclick = () => exportToPdf();
                } else {
                    exportCsvBtn.classList.add('d-none');
                    exportPdfBtn.classList.add('d-none');
                }
                
            } else {
                // Erreur 400 côté serveur (Validation)
                let errorMsg = data.question ? data.question[0] : "Une erreur s'est produite lors de la validation.";
                appendMessage(`Erreur : ${errorMsg}`, 'bot-msg text-danger', '<i class="bi bi-exclamation-triangle me-2"></i>Erreur');
            }
        } catch (error) {
            console.error('Erreur Fetch:', error);
            appendMessage("Erreur de connexion au serveur. Veuillez vérifier votre réseau.", 'bot-msg text-danger', '<i class="bi bi-wifi-off me-2"></i>Erreur');
        } finally {
            // Cacher le loader et réactiver l'input
            loader.classList.add('d-none');
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
            
            // Scroll to bottom
            historyContainer.scrollTop = historyContainer.scrollHeight;
        }
    });

    function appendMessage(text, className, header) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `${className} msg-bubble shadow-sm p-3 rounded mb-3`;
        msgDiv.innerHTML = `<strong>${header}</strong><br>${text}`;
        historyContainer.appendChild(msgDiv);
    }

    function updateTable(tableData) {
        tableBody.innerHTML = '';
        const tableHead = document.getElementById('tableHead');
        
        if (!tableData || tableData.length === 0) {
            tableHead.innerHTML = `
                <th class="text-muted fw-normal">Région</th>
                <th class="text-muted fw-normal">Année</th>
                <th class="text-muted fw-normal">Valeur</th>
            `;
            tableBody.innerHTML = '<tr><td colspan="3" class="text-muted small py-3">Aucune donnée trouvée.</td></tr>';
            return;
        }
        
        // Génération dynamique des en-têtes (Supporte les sommes/moyennes avec opération, indicateur, valeur)
        const keys = Object.keys(tableData[0]);
        tableHead.innerHTML = keys.map(k => `<th class="text-muted fw-normal text-capitalize">${k}</th>`).join('');
        
        tableData.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = keys.map(k => {
                const val = row[k];
                const displayVal = (typeof val === 'number' && !Number.isInteger(val)) ? val.toFixed(2) : val;
                return `<td>${displayVal}</td>`;
            }).join('');
            tableBody.appendChild(tr);
        });
    }

    function updateChart(chartConfig) {
        // Règle stricte du lab: Destruction propre du graphique précédent
        if (chartInstance) {
            chartInstance.destroy();
            chartInstance = null;
        }
        
        const canvas = document.getElementById('resultChart');
        const ctx = canvas.getContext('2d');
        
        if (!chartConfig) {
            emptyChartMsg.style.display = 'block';
            return;
        }
        
        emptyChartMsg.style.display = 'none';
        
        // Ajustement des couleurs selon le thème
        const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
        const textColor = isDark ? '#f8f9fa' : '#2b3035';
        const gridColor = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)';
        
        // Palette de couleurs pour les comparaisons
        const colors = [
            'rgba(13, 110, 253, 0.7)',   // Primary
            'rgba(25, 135, 84, 0.7)',    // Success
            'rgba(220, 53, 69, 0.7)',    // Danger
            'rgba(255, 193, 7, 0.7)',    // Warning
            'rgba(13, 202, 240, 0.7)',   // Info
            'rgba(102, 16, 242, 0.7)'    // Indigo
        ];
        
        // Ajout de styles pour tous les datasets
        chartConfig.datasets.forEach((dataset, index) => {
            const color = colors[index % colors.length];
            const solidColor = color.replace('0.7)', '1)');
            
            if (chartConfig.type === 'line') {
                let gradient = ctx.createLinearGradient(0, 0, 0, 400);
                gradient.addColorStop(0, color.replace('0.7)', '0.5)'));
                gradient.addColorStop(1, color.replace('0.7)', '0.0)'));
                
                dataset.backgroundColor = gradient;
                dataset.fill = true;
                dataset.borderColor = solidColor;
                dataset.pointBackgroundColor = '#ffffff';
                dataset.pointBorderColor = solidColor;
                dataset.pointBorderWidth = 2;
                dataset.pointRadius = 4;
                dataset.pointHoverRadius = 6;
            } else {
                dataset.backgroundColor = color;
                dataset.borderColor = solidColor;
                dataset.borderRadius = 4;
                dataset.borderWidth = 0;
                dataset.hoverBackgroundColor = solidColor;
            }
        });
        
        chartInstance = new Chart(ctx, {
            type: chartConfig.type,
            data: {
                labels: chartConfig.labels,
                datasets: chartConfig.datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                },
                plugins: {
                    legend: {
                        labels: { color: textColor, font: { family: "'Inter', sans-serif", size: 13 } }
                    },
                    tooltip: {
                        backgroundColor: isDark ? 'rgba(255,255,255,0.9)' : 'rgba(0,0,0,0.8)',
                        titleColor: isDark ? '#000' : '#fff',
                        bodyColor: isDark ? '#000' : '#fff',
                        padding: 10,
                        cornerRadius: 8,
                        displayColors: false
                    }
                },
                scales: {
                    x: { 
                        ticks: { color: textColor, font: { family: "'Inter', sans-serif" } }, 
                        grid: { color: gridColor, drawBorder: false } 
                    },
                    y: { 
                        ticks: { color: textColor, font: { family: "'Inter', sans-serif" } }, 
                        grid: { color: gridColor, drawBorder: false } 
                    }
                }
            }
        });
    }

    function initMap() {
        // Centré sur le Sénégal
        mapInstance = L.map('senegalMap').setView([14.4974, -14.4524], 6);
        
        // Ajout des tuiles (Fond de carte OpenStreetMap)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(mapInstance);
        
        // Créer un calque pour nos marqueurs dynamiques
        mapLayerGroup = L.layerGroup().addTo(mapInstance);
    }

    function updateMap(tableData, indicatorName) {
        if (!mapInstance || !mapLayerGroup) return;
        
        // Vider les anciens marqueurs
        mapLayerGroup.clearLayers();
        
        if (!tableData || tableData.length === 0) return;
        
        // Si c'est une somme ou moyenne sans dimension géographique, on passe
        if (tableData.length === 1 && !tableData[0].region) return;

        // Trouver la valeur max pour calculer la taille des cercles
        const values = tableData.map(row => {
            const keys = Object.keys(row).filter(k => k !== 'region' && k !== 'annee');
            return row[keys[0]];
        }).filter(v => typeof v === 'number');
        
        const maxVal = values.length > 0 ? Math.max(...values) : 1;

        tableData.forEach(row => {
            const rName = row.region;
            if (regionCoords[rName]) {
                const keys = Object.keys(row).filter(k => k !== 'region' && k !== 'annee');
                const val = row[keys[0]];
                
                // Calculer le rayon relatif
                const isNumber = typeof val === 'number';
                const radius = isNumber ? Math.max(5000, (val / maxVal) * 30000) : 10000;
                
                const circle = L.circle(regionCoords[rName], {
                    color: '#0d6efd',
                    fillColor: '#0d6efd',
                    fillOpacity: 0.5,
                    radius: radius
                });
                
                const displayVal = (isNumber && !Number.isInteger(val)) ? val.toFixed(2) : val;
                const label = indicatorName ? indicatorName.replace('_pct', ' (%)').replace('_', ' ') : 'Valeur';
                
                circle.bindPopup(`<strong>${rName}</strong><br>${label}: ${displayVal}`);
                circle.addTo(mapLayerGroup);
            }
        });
    }

    // Bonus : Export CSV
    function exportToCsv(tableData) {
        if(!tableData || tableData.length === 0) return;
        
        const keys = Object.keys(tableData[0]);
        let csvContent = "data:text/csv;charset=utf-8," 
            + keys.join(",") + "\n"
            + tableData.map(row => keys.map(k => row[k]).join(",")).join("\n");
            
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "export_senstat.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } // <- fermeture de exportToCsv
    
    // Export PDF
    function exportToPdf() {
        // Cibler la zone de visualisation (col-md-7)
        const element = document.querySelector('.col-md-7');
        const opt = {
            margin:       10,
            filename:     'Rapport_SenStat.pdf',
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2, useCORS: true },
            jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };
        
        // Ajouter un titre temporaire
        const title = document.createElement('h3');
        title.innerHTML = 'Rapport Statistique - SenStat AI';
        title.style.textAlign = 'center';
        title.style.marginBottom = '20px';
        element.prepend(title);
        
        html2pdf().set(opt).from(element).save().then(() => {
            element.removeChild(title);
        });
    }
    
    // Gestion des suggestions
    document.querySelectorAll('.badge-suggestion').forEach(badge => {
        badge.addEventListener('click', (e) => {
            const q = e.target.getAttribute('data-question');
            if(q) {
                input.value = q;
                input.focus();
                input.classList.add('bg-warning', 'bg-opacity-25');
                setTimeout(() => input.classList.remove('bg-warning', 'bg-opacity-25'), 300);
            }
        });
    });

    // --- Web Speech API (Chat Vocal) ---
    const micBtn = document.getElementById('micBtn');
    const micIcon = document.getElementById('micIcon');
    let isRecording = false;
    let synth = window.speechSynthesis;

    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        micBtn.style.display = 'none'; // Cacher si non supporté
        console.warn("L'API Web Speech n'est pas supportée par ce navigateur.");
    } else {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = 'fr-FR';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = function() {
            isRecording = true;
            micIcon.classList.replace('bi-mic-fill', 'bi-mic-mute-fill');
            micBtn.classList.add('recording');
            input.placeholder = "Écoute en cours...";
            if (synth) synth.cancel(); // Couper la voix si le bot parle
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            input.value = transcript;
            stopRecordingUI();
            form.dispatchEvent(new Event('submit')); // Soumettre automatiquement
        };

        recognition.onerror = function(event) {
            console.error('Erreur vocale :', event.error);
            stopRecordingUI();
            appendMessage("Erreur d'écoute vocale : " + event.error, 'bot-msg text-danger', '<i class="bi bi-exclamation-triangle me-2"></i>Erreur');
        };

        recognition.onend = function() {
            stopRecordingUI();
        };

        micBtn.addEventListener('click', () => {
            if (isRecording) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
    }

    function stopRecordingUI() {
        isRecording = false;
        if (micIcon.classList.contains('bi-mic-mute-fill')) {
            micIcon.classList.replace('bi-mic-mute-fill', 'bi-mic-fill');
        }
        micBtn.classList.remove('recording');
        input.placeholder = "Demandez une statistique...";
    }

    function speakText(text) {
        if (!synth) return;
        synth.cancel();
        
        // Nettoyer le HTML pour la lecture
        const tempDiv = document.createElement("div");
        tempDiv.innerHTML = text;
        const cleanText = tempDiv.textContent || tempDiv.innerText || "";
        
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = 'fr-FR';
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        synth.speak(utterance);
    }
});

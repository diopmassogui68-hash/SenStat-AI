/* 
 * SenStat AI - Logique Frontend Principale
 * Auteur: Serigne Mbacke Faye (Cœur JS) & Sanor Mangane (Bonus)
 */

let chartInstance = null;

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
    
    // Web Speech API globals
    let synth = window.speechSynthesis;
    let isVoiceEnabled = true; // Permet de désactiver la voix si désiré
    
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
                
                appendMessage(msgHtml, 'bot-msg', '<i class="bi bi-robot me-2"></i>SenStat AI');
                
                // Synthèse vocale de la réponse
                speakText(data.answer);
                
                // Mettre à jour le tableau
                updateTable(data.table);
                
                // Mettre à jour le graphique (Destruction propre)
                updateChart(data.chart);
                
                // Activer l'export CSV si données
                if(data.table && data.table.length > 0) {
                    exportCsvBtn.classList.remove('d-none');
                    exportCsvBtn.onclick = () => exportToCsv(data.table);
                } else {
                    exportCsvBtn.classList.add('d-none');
                }
                
            } else {
                // Erreur 400 côté serveur (Validation)
                let errorMsg = data.question ? data.question[0] : "Une erreur s'est produite lors de la validation.";
                appendMessage(`Erreur : ${errorMsg}`, 'bot-msg text-danger', '<i class="bi bi-exclamation-triangle me-2"></i>Erreur');
                speakText(`Erreur : ${errorMsg}`);
            }
        } catch (error) {
            console.error('Erreur Fetch:', error);
            appendMessage("Erreur de connexion au serveur. Veuillez vérifier votre réseau.", 'bot-msg text-danger', '<i class="bi bi-wifi-off me-2"></i>Erreur');
            speakText("Erreur de connexion au serveur.");
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

    // --- Bonus Vocal : Web Speech API ---
    const micBtn = document.getElementById('micBtn');
    const micIcon = document.getElementById('micIcon');
    let recognition = null;
    let isRecording = false;

    if (micBtn && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'fr-FR';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = function() {
            isRecording = true;
            micIcon.classList.replace('bi-mic-fill', 'bi-mic-mute-fill');
            micBtn.classList.replace('btn-outline-primary', 'btn-danger');
            input.placeholder = "Écoute en cours...";
            if (synth) synth.cancel(); // Couper la voix si le bot parle
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            input.value = transcript;
            form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        };

        recognition.onerror = function(event) {
            console.error("Erreur de reconnaissance vocale:", event.error);
            stopRecordingUI();
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
    } else if (micBtn) {
        micBtn.style.display = 'none'; // Cacher si non supporté
    }

    function stopRecordingUI() {
        isRecording = false;
        if (micIcon.classList.contains('bi-mic-mute-fill')) {
            micIcon.classList.replace('bi-mic-mute-fill', 'bi-mic-fill');
        }
        if (micBtn.classList.contains('btn-danger')) {
            micBtn.classList.replace('btn-danger', 'btn-outline-primary');
        }
        input.placeholder = "Ex: Évolution du chômage à Dakar ?";
    }

    function speakText(text) {
        if (!synth || !isVoiceEnabled) return;
        synth.cancel();
        // Nettoyer le HTML pour la lecture
        const cleanText = text.replace(/<[^>]*>?/gm, '');
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = 'fr-FR';
        utterance.rate = 1.0;
        synth.speak(utterance);
    }
});

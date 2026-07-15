/* 
 * SenStat AI - Logique Frontend Principale
 * Auteur: Serigne Mbacke Faye (Cœur JS) & Sanor Mangane (Bonus)
 */

let chartInstance = null;
let chatHistoryData = []; // Bonus: Historique de session client

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
                
                // Bonus 1: Comment j'ai compris votre question
                if(data.metadata && data.metadata.intent_debug) {
                    const intent = data.metadata.intent_debug;
                    const regionsStr = intent.regions.length > 0 ? intent.regions.join(', ') : 'Toutes';
                    const yearsStr = intent.start_year ? (intent.start_year === intent.end_year ? intent.start_year : `${intent.start_year} - ${intent.end_year}`) : 'Non spécifié';
                    
                    msgHtml += `
                        <div class="intent-details mt-2">
                            <strong><i class="bi bi-info-circle me-1"></i>Analyse :</strong> 
                            Indicateur: <em>${intent.indicator || '?'}</em> | 
                            Région(s): <em>${regionsStr}</em> | 
                            Année(s): <em>${yearsStr}</em> | 
                            Action: <em>${intent.operation}</em>
                        </div>
                    `;
                }

                appendMessage(msgHtml, 'bot-msg', '<i class="bi bi-robot me-2"></i>SenStat AI');
                
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
                
                // Sauvegarder dans la session client (Bonus)
                chatHistoryData.push({ question, answer: data.answer });
                
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
        if (!tableData || tableData.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="3" class="text-muted small py-3">Aucune donnée trouvée.</td></tr>';
            return;
        }
        
        tableData.forEach(row => {
            // Trouver la clé de l'indicateur dynamiquement
            const keys = Object.keys(row).filter(k => k !== 'region' && k !== 'annee');
            const valueKey = keys[0];
            const val = row[valueKey];
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.region}</td>
                <td>${row.annee}</td>
                <td class="fw-bold">${typeof val === 'number' && !Number.isInteger(val) ? val.toFixed(2) : val}</td>
            `;
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
        
        // Ajout d'un dégradé pour les graphiques de type "line"
        if (chartConfig.type === 'line' && chartConfig.datasets.length > 0) {
            let gradient = ctx.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, 'rgba(13, 110, 253, 0.5)');
            gradient.addColorStop(1, 'rgba(13, 110, 253, 0.0)');
            chartConfig.datasets[0].backgroundColor = gradient;
            chartConfig.datasets[0].fill = true;
            chartConfig.datasets[0].borderColor = '#0d6efd';
            chartConfig.datasets[0].pointBackgroundColor = '#ffffff';
            chartConfig.datasets[0].pointBorderColor = '#0d6efd';
            chartConfig.datasets[0].pointBorderWidth = 2;
            chartConfig.datasets[0].pointRadius = 4;
            chartConfig.datasets[0].pointHoverRadius = 6;
        } else if (chartConfig.datasets.length > 0) {
            // Amélioration des bar charts
            chartConfig.datasets[0].backgroundColor = 'rgba(13, 110, 253, 0.7)';
            chartConfig.datasets[0].borderColor = '#0d6efd';
            chartConfig.datasets[0].borderRadius = 4;
            chartConfig.datasets[0].borderWidth = 0;
            chartConfig.datasets[0].hoverBackgroundColor = 'rgba(13, 110, 253, 1)';
        }
        
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
    }
});

// Fonction globale pour les suggestions
window.setQuestion = function(q) {
    const input = document.getElementById('questionInput');
    input.value = q;
    input.focus();
    // Animation visuelle courte
    input.classList.add('bg-warning', 'bg-opacity-25');
    setTimeout(() => input.classList.remove('bg-warning', 'bg-opacity-25'), 300);
}

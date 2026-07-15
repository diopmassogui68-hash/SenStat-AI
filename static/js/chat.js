document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    const chatForm = document.getElementById('chat-form');
    const questionInput = document.getElementById('question-input');
    const chatHistory = document.getElementById('chat-history');
    const sendButton = document.getElementById('send-button');
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const suggestionBtns = document.querySelectorAll('.suggestion-btn');

    // --- Templates ---
    const userMessageTemplate = document.getElementById('user-message-template');
    const botMessageTemplate = document.getElementById('bot-message-template');
    const loadingTemplate = document.getElementById('loading-template');

    // --- Global State ---
    let currentChartInstance = null; // To properly destroy previous chart

    // --- Theme Management (Dark Mode) ---
    const initTheme = () => {
        const savedTheme = localStorage.getItem('senstat-theme') || 'light';
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
        updateThemeIcon(savedTheme);
    };

    const updateThemeIcon = (theme) => {
        if (theme === 'dark') {
            themeIcon.className = 'bi bi-sun-fill';
        } else {
            themeIcon.className = 'bi bi-moon-stars-fill';
        }
    };

    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('senstat-theme', newTheme);
        updateThemeIcon(newTheme);

        // Update existing chart colors if needed (Bonus)
        if (currentChartInstance) {
            Chart.defaults.color = newTheme === 'dark' ? '#adb5bd' : '#6c757d';
            currentChartInstance.update();
        }
    });

    initTheme();
    Chart.defaults.color = document.documentElement.getAttribute('data-bs-theme') === 'dark' ? '#adb5bd' : '#6c757d';
    Chart.defaults.font.family = 'Inter, sans-serif';

    // --- Helper Functions ---
    const scrollToBottom = () => {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    };

    const toggleInputState = (disabled) => {
        questionInput.disabled = disabled;
        sendButton.disabled = disabled;
        if (!disabled) {
            questionInput.focus();
        }
    };

    // --- Message Rendering ---
    const appendUserMessage = (text) => {
        const clone = userMessageTemplate.content.cloneNode(true);
        clone.querySelector('.user-text').textContent = text;
        chatHistory.appendChild(clone);
        scrollToBottom();
    };

    const appendLoading = () => {
        const clone = loadingTemplate.content.cloneNode(true);
        const node = clone.querySelector('.loading-message');
        chatHistory.appendChild(clone);
        scrollToBottom();
        return node;
    };

    const renderBotResponse = (data, loadingNode) => {
        // Remove loading indicator
        if (loadingNode && loadingNode.parentNode) {
            loadingNode.parentNode.removeChild(loadingNode);
        }

        const clone = botMessageTemplate.content.cloneNode(true);
        const messageContainer = clone.querySelector('.bot-message');
        
        // 1. Text Answer
        clone.querySelector('.answer-text').textContent = data.answer;

        // 2. Intent Block (Bonus visuel)
        if (data.intent) {
            const intentBlock = clone.querySelector('.intent-block');
            const intentText = clone.querySelector('.intent-text');
            intentBlock.classList.remove('d-none');
            
            let intentStr = `Opération: ${data.intent.operation || 'Valeur'} | Indicateur: ${data.intent.indicator}`;
            if (data.intent.regions && data.intent.regions.length > 0) {
                intentStr += ` | Région(s): ${data.intent.regions.join(', ')}`;
            }
            if (data.intent.start_year) {
                intentStr += ` | Année(s): ${data.intent.start_year}` + (data.intent.end_year && data.intent.end_year !== data.intent.start_year ? ` - ${data.intent.end_year}` : '');
            }
            intentText.textContent = intentStr;
        }

        // 3. Table Data
        if (data.table && data.table.length > 0) {
            const tableBlock = clone.querySelector('.table-block');
            tableBlock.classList.remove('d-none');
            
            const thead = clone.querySelector('.table-headers');
            const tbody = clone.querySelector('.table-body');
            
            // Generate Headers
            const keys = Object.keys(data.table[0]);
            keys.forEach(key => {
                const th = document.createElement('th');
                th.textContent = key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');
                thead.appendChild(th);
            });

            // Generate Rows
            data.table.forEach(row => {
                const tr = document.createElement('tr');
                keys.forEach(key => {
                    const td = document.createElement('td');
                    td.textContent = row[key];
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
        }

        // 4. Chart.js (Destruction propre et recréation)
        if (data.chart && data.chart.type) {
            const chartBlock = clone.querySelector('.chart-block');
            chartBlock.classList.remove('d-none');
            const canvas = clone.querySelector('.chart-canvas');
            
            // Destroy previous instance to save memory & prevent glitches
            if (currentChartInstance) {
                currentChartInstance.destroy();
            }

            // Generate unique ID for the canvas (though not strictly required with object references)
            canvas.id = 'chart-' + Date.now();
            
            // Append clone first so canvas has dimensions
            chatHistory.appendChild(clone);
            
            const ctx = document.getElementById(canvas.id).getContext('2d');
            currentChartInstance = new Chart(ctx, {
                type: data.chart.type,
                data: {
                    labels: data.chart.labels,
                    datasets: data.chart.datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        } else {
            chatHistory.appendChild(clone);
        }

        // 5. Metadata
        if (data.metadata) {
            // Find the recently appended message metadata
            const messages = chatHistory.querySelectorAll('.bot-message');
            const latestMessage = messages[messages.length - 1];
            
            const metaBlock = latestMessage.querySelector('.metadata-block');
            const rowsUsed = latestMessage.querySelector('.rows-used');
            
            metaBlock.classList.remove('d-none');
            rowsUsed.textContent = data.metadata.rows_used || 0;
        }

        scrollToBottom();
    };

    // --- Mock API Logic (Waiting for Backend) ---
    const generateMockResponse = (question) => {
        return new Promise((resolve) => {
            setTimeout(() => {
                const q = question.toLowerCase();
                let response = {};

                if (q.includes('dakar') && q.includes('internet')) {
                    response = {
                        answer: "En 2023, le taux d'accès à internet à Dakar était de 85%.",
                        table: [{ region: "Dakar", annee: 2023, acces_internet_pct: 85 }],
                        chart: null,
                        metadata: { fictitious: true, rows_used: 1 },
                        intent: { operation: "value", indicator: "acces_internet_pct", regions: ["Dakar"], start_year: 2023 }
                    };
                } else if (q.includes('compare') || q.includes('chômage')) {
                    response = {
                        answer: "Voici la comparaison du taux de chômage entre Dakar et Thiès en 2022.",
                        table: [
                            { region: "Dakar", annee: 2022, taux_chomage_pct: 12.5 },
                            { region: "Thiès", annee: 2022, taux_chomage_pct: 14.2 }
                        ],
                        chart: {
                            type: "bar",
                            labels: ["Dakar", "Thiès"],
                            datasets: [{
                                label: "Taux de chômage (%)",
                                data: [12.5, 14.2],
                                backgroundColor: ["rgba(13, 110, 253, 0.7)", "rgba(25, 135, 84, 0.7)"]
                            }]
                        },
                        metadata: { fictitious: true, rows_used: 2 },
                        intent: { operation: "compare", indicator: "taux_chomage_pct", regions: ["Dakar", "Thiès"], start_year: 2022 }
                    };
                } else if (q.includes('évolution') || q.includes('production')) {
                    response = {
                        answer: "L'évolution de la production céréalière à Diourbel montre une tendance à la hausse de 2020 à 2024.",
                        table: [
                            { annee: 2020, production_cerealiere_tonnes: 45000 },
                            { annee: 2021, production_cerealiere_tonnes: 48000 },
                            { annee: 2022, production_cerealiere_tonnes: 46500 },
                            { annee: 2023, production_cerealiere_tonnes: 52000 },
                            { annee: 2024, production_cerealiere_tonnes: 55000 }
                        ],
                        chart: {
                            type: "line",
                            labels: ["2020", "2021", "2022", "2023", "2024"],
                            datasets: [{
                                label: "Production (Tonnes)",
                                data: [45000, 48000, 46500, 52000, 55000],
                                borderColor: "rgba(13, 110, 253, 1)",
                                tension: 0.3,
                                fill: true,
                                backgroundColor: "rgba(13, 110, 253, 0.1)"
                            }]
                        },
                        metadata: { fictitious: true, rows_used: 5 },
                        intent: { operation: "trend", indicator: "production_cerealiere_tonnes", regions: ["Diourbel"], start_year: 2020, end_year: 2024 }
                    };
                } else {
                    response = {
                        answer: "Voici les informations générales trouvées concernant votre demande.",
                        table: [
                            { region: "Moyenne Nationale", annee: 2024, indicateur_moyen: 45.5 }
                        ],
                        chart: null,
                        metadata: { fictitious: true, rows_used: 14 },
                        intent: { operation: "average", indicator: "inconnu" }
                    };
                }

                resolve(response);
            }, 1200); // Simulate network latency
        });
    };

    // --- Event Listeners ---
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const text = questionInput.value.trim();
        if (!text) return;

        // 1. Show user message
        appendUserMessage(text);
        questionInput.value = '';
        
        // 2. State & Loading
        toggleInputState(true);
        const loadingNode = appendLoading();

        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
            const res = await fetch('/api/question/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ text })
            });
            
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            const data = await res.json();
            
            // 3. Render Response
            renderBotResponse(data, loadingNode);

        } catch (error) {
            console.error("Erreur API:", error);
            renderBotResponse({
                answer: "Désolé, une erreur s'est produite lors de la connexion au serveur.",
                table: [],
                chart: null,
                metadata: { rows_used: 0 }
            }, loadingNode);
        } finally {
            toggleInputState(false);
        }
    });

    // Suggestions click handler
    suggestionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const text = btn.textContent.trim();
            questionInput.value = text;
            chatForm.dispatchEvent(new Event('submit'));
        });
    });
});

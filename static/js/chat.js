/**
 * Logique Frontend - Cœur (Serigne Mbacke Faye)
 * Étape 7 : Interface conversationnelle, appel API, gestion Chart.js et gestion d'erreurs lisible.
 */

let currentChart = null;

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('questionForm');
    const input = document.getElementById('questionInput');
    const sendBtn = document.getElementById('sendBtn');
    const historyDiv = document.getElementById('chatHistory');
    const loader = document.getElementById('loadingIndicator');
    const tableHead = document.getElementById('tableHead');
    const tableBody = document.getElementById('tableBody');
    const emptyChartMsg = document.getElementById('emptyChartMsg');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const question = input.value.trim();
        if (!question) return;

        // 1. Ajout de la question de l'utilisateur
        appendMessage(question, 'message-user');
        input.value = '';
        input.disabled = true;
        sendBtn.disabled = true;
        loader.classList.remove('d-none');

        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            
            // 2. Appel à l'API
            const response = await fetch('/api/question/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ question: question })
            });

            const data = await response.json();

            // 3. Gestion d'erreurs lisible
            if (!response.ok) {
                const errorText = data.question ? data.question[0] : "Erreur de traitement sur le serveur.";
                appendMessage(`Erreur : ${errorText}`, 'message-bot text-danger');
                return;
            }

            // 4. Affichage de la réponse texte
            appendMessage(data.answer, 'message-bot');

            // 5. Mise à jour du tableau
            updateTable(data.table);

            // 6. Gestion du cycle de vie Chart.js
            updateChart(data.chart);

        } catch (error) {
            console.error("Erreur réseau :", error);
            appendMessage("Erreur de connexion au serveur. Vérifiez votre réseau.", 'message-bot text-danger');
        } finally {
            loader.classList.add('d-none');
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
            historyDiv.scrollTop = historyDiv.scrollHeight;
        }
    });

    function appendMessage(text, cssClass) {
        const div = document.createElement('div');
        div.className = `message ${cssClass}`;
        div.textContent = text;
        historyDiv.appendChild(div);
    }

    function updateTable(tableData) {
        tableHead.innerHTML = '';
        tableBody.innerHTML = '';

        if (!tableData || tableData.length === 0) {
            tableHead.innerHTML = '<tr><th>Région</th><th>Année</th><th>Valeur</th></tr>';
            tableBody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">Aucune donnée trouvée.</td></tr>';
            return;
        }

        // Génération dynamique des colonnes
        const keys = Object.keys(tableData[0]);
        const trHead = document.createElement('tr');
        keys.forEach(k => {
            const th = document.createElement('th');
            // Capitaliser la première lettre
            th.textContent = k.charAt(0).toUpperCase() + k.slice(1);
            trHead.appendChild(th);
        });
        tableHead.appendChild(trHead);

        // Lignes de données
        tableData.forEach(row => {
            const tr = document.createElement('tr');
            keys.forEach(k => {
                const td = document.createElement('td');
                const val = row[k];
                // Formater les nombres à virgule flottante
                td.textContent = (typeof val === 'number' && !Number.isInteger(val)) ? val.toFixed(2) : val;
                tr.appendChild(td);
            });
            tableBody.appendChild(tr);
        });
    }

    function updateChart(chartConfig) {
        const canvas = document.getElementById('resultChart');
        const ctx = canvas.getContext('2d');

        // EXIGENCE STRICTE : Destruction de l'instance précédente pour éviter la superposition
        if (currentChart) {
            currentChart.destroy();
            currentChart = null;
        }

        if (!chartConfig) {
            emptyChartMsg.style.display = 'block';
            return;
        }

        emptyChartMsg.style.display = 'none';

        // Palette de base pour les graphiques de type "compare" ou "ranking"
        const colors = [
            'rgba(13, 110, 253, 0.7)',
            'rgba(25, 135, 84, 0.7)',
            'rgba(220, 53, 69, 0.7)',
            'rgba(255, 193, 7, 0.7)',
            'rgba(13, 202, 240, 0.7)'
        ];

        // S'assurer que tous les datasets ont des couleurs
        chartConfig.datasets.forEach((dataset, index) => {
            const color = colors[index % colors.length];
            if (chartConfig.type === 'line') {
                dataset.borderColor = color.replace('0.7)', '1)');
                dataset.backgroundColor = color.replace('0.7)', '0.1)');
                dataset.fill = true;
                dataset.tension = 0.1;
            } else {
                dataset.backgroundColor = color;
                dataset.borderColor = color.replace('0.7)', '1)');
                dataset.borderWidth = 1;
            }
        });

        // Création de la nouvelle instance
        currentChart = new Chart(ctx, {
            type: chartConfig.type,
            data: {
                labels: chartConfig.labels,
                datasets: chartConfig.datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
});

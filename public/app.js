/**
 * Boijelux v7 - Complete Frontend Logic
 * Deployed at: https://ai.taagc.site
 */

const API_BASE = '/api';
const DOMAIN = 'ai.taagc.site';
const APP_VERSION = '7.0.0';
let refreshTimer = null;
let settings = {};

// ============================================
// 1. INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log(`🚀 Boijelux v${APP_VERSION} - ${DOMAIN}`);
    loadSettings();
    loadAllData();
    setupNavigation();
    setupAutoRefresh();
    setupKeyboardShortcuts();
});

// ============================================
// 2. NAVIGATION
// ============================================

function setupNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById(`page-${page}`).classList.add('active');
            document.getElementById('navLinks').classList.remove('open');
        });
    });
}

function toggleMobileNav() {
    document.getElementById('navLinks').classList.toggle('open');
}

// ============================================
// 3. LOAD ALL DATA
// ============================================

function loadAllData() {
    loadStats();
    loadStatus();
    loadTasks();
    loadAllTasks();
    loadBots();
    loadKnowledge();
    loadSystemStatus();
}

// ============================================
// 4. LOAD STATS
// ============================================

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        if (data.status === 'success') {
            const agent = data.agent || {};
            document.getElementById('statTasks').textContent = agent.tasks_completed || 0;
            document.getElementById('statDomains').textContent = agent.domains?.length || 14;
            document.getElementById('statKnowledge').textContent = 0;
            document.getElementById('statBots').textContent = agent.bots_created || 0;
            document.getElementById('statUptime').textContent = formatUptime(agent.uptime || 0);
            document.getElementById('statVersion').textContent = agent.version || APP_VERSION;
            document.getElementById('statusDot').className = 'status-dot online';
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        document.getElementById('statusDot').className = 'status-dot offline';
    }
}

// ============================================
// 5. LOAD STATUS
// ============================================

async function loadStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        if (data.status === 'success') {
            displayStatus(data);
        } else {
            displayError('statusContainer', 'Failed to load status');
        }
    } catch (error) {
        displayError('statusContainer', 'Error: ' + error.message);
    }
}

function displayStatus(data) {
    const container = document.getElementById('statusContainer');
    const agent = data.agent || {};
    container.innerHTML = `
        <div class="status-grid">
            <div><strong>Domain:</strong> ${data.domain || DOMAIN}</div>
            <div><strong>State:</strong> ${agent.state || 'online'}</div>
            <div><strong>Tasks:</strong> ${agent.tasks_completed || 0}</div>
            <div><strong>Domains:</strong> ${agent.domains?.length || 0}</div>
            <div><strong>Bots:</strong> ${agent.bots_created || 0}</div>
            <div><strong>Uptime:</strong> ${formatUptime(agent.uptime || 0)}</div>
            <div><strong>Capabilities:</strong> ${agent.capabilities?.length || 0}</div>
            <div><strong>Version:</strong> ${agent.version || APP_VERSION}</div>
        </div>
    `;
}

function formatUptime(seconds) {
    if (seconds < 60) return Math.floor(seconds) + 's';
    if (seconds < 3600) return Math.floor(seconds / 60) + 'm';
    if (seconds < 86400) return Math.floor(seconds / 3600) + 'h';
    return Math.floor(seconds / 86400) + 'd';
}

// ============================================
// 6. TASKS
// ============================================

async function loadTasks() {
    try {
        const response = await fetch(`${API_BASE}/tasks`);
        const data = await response.json();
        if (data.status === 'success') {
            displayTasks(data.tasks, data.count);
        }
    } catch (error) {
        displayError('tasksContainer', 'Error: ' + error.message);
    }
}

function displayTasks(tasks, count) {
    const container = document.getElementById('tasksContainer');
    if (!tasks || tasks.length === 0) {
        container.innerHTML = `<div class="empty-state"><span class="icon">📋</span><p>No tasks yet</p></div>`;
        return;
    }
    let html = `<div class="task-count">📋 ${count || tasks.length} tasks</div>`;
    tasks.slice(-5).reverse().forEach(task => {
        const statusClass = task.status || 'pending';
        html += `
            <div class="task-item">
                <div class="task-header">
                    <span class="task-priority">Priority: ${task.priority || 3}</span>
                    <span class="task-status ${statusClass}">${statusClass}</span>
                </div>
                <div class="task-description">${task.description || 'No description'}</div>
                <div class="task-meta">
                    <span>🕐 ${formatDate(task.created)}</span>
                    ${task.completed ? `<span>✅ ${formatDate(task.completed)}</span>` : ''}
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

async function loadAllTasks() {
    try {
        const response = await fetch(`${API_BASE}/tasks`);
        const data = await response.json();
        if (data.status === 'success') {
            displayAllTasks(data.tasks, data.count);
        }
    } catch (error) { console.error('Error loading all tasks:', error); }
}

function displayAllTasks(tasks, count) {
    const container = document.getElementById('allTasksContainer');
    if (!tasks || tasks.length === 0) {
        container.innerHTML = `<div class="empty-state"><span class="icon">📋</span><p>No tasks found</p></div>`;
        return;
    }
    let html = `<div class="task-count">📋 Total: ${count || tasks.length} tasks</div>`;
    tasks.slice().reverse().forEach(task => {
        const statusClass = task.status || 'pending';
        html += `
            <div class="task-item">
                <div class="task-header">
                    <span class="task-priority">Priority: ${task.priority || 3}</span>
                    <span class="task-status ${statusClass}">${statusClass}</span>
                </div>
                <div class="task-description">${task.description || 'No description'}</div>
                <div class="task-meta">
                    <span>🕐 ${formatDate(task.created)}</span>
                    ${task.completed ? `<span>✅ ${formatDate(task.completed)}</span>` : ''}
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

// ============================================
// 7. PROCESS TASK
// ============================================

async function processTask() {
    const input = document.getElementById('taskInput');
    const priority = document.getElementById('taskPriority');
    const useInternet = document.getElementById('taskInternet')?.checked || false;
    const task = input.value.trim();
    const resultDiv = document.getElementById('taskResult');
    const btn = document.querySelector('#page-tasks .task-form button');
    
    if (!task) { showResult(resultDiv, '❌ Please enter a task', 'error'); return; }
    
    btn.disabled = true;
    btn.textContent = '⏳ Processing...';
    resultDiv.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/task`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                task: task,
                context: {
                    priority: parseInt(priority.value),
                    use_internet: useInternet
                }
            })
        });
        const data = await response.json();
        if (data.status === 'success') {
            showResult(resultDiv, `
✅ Task processed successfully!

📋 Task: ${task}
🌐 Internet: ${useInternet ? 'Enabled' : 'Disabled'}
🎯 Result: ${data.result?.success ? 'Success' : 'Failed'}

${JSON.stringify(data.result, null, 2)}
            `, 'success');
            loadAllData();
            input.value = '';
        } else {
            showResult(resultDiv, `❌ Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showResult(resultDiv, `❌ Error: ${error.message}`, 'error');
    }
    btn.disabled = false;
    btn.textContent = '▶ Process Task';
}

async function processQuickTask() {
    const input = document.getElementById('quickTaskInput');
    const task = input.value.trim();
    const resultDiv = document.getElementById('quickTaskResult');
    const btn = document.querySelector('.quick-task button');
    
    if (!task) { showResult(resultDiv, '❌ Please enter a task', 'error'); return; }
    
    btn.disabled = true;
    btn.textContent = '⏳...';
    resultDiv.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/task`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task, context: { use_internet: true } })
        });
        const data = await response.json();
        if (data.status === 'success') {
            showResult(resultDiv, `✅ ${task}\n${JSON.stringify(data.result, null, 2)}`, 'success');
            loadAllData();
            input.value = '';
        } else {
            showResult(resultDiv, `❌ ${data.message}`, 'error');
        }
    } catch (error) {
        showResult(resultDiv, `❌ ${error.message}`, 'error');
    }
    btn.disabled = false;
    btn.textContent = '▶ Execute';
}

// ============================================
// 8. CREATE BOT
// ============================================

async function createBot() {
    const requirements = document.getElementById('botRequirements').value.trim();
    const location = document.getElementById('botLocation').value;
    const name = document.getElementById('botName').value.trim();
    const resultDiv = document.getElementById('botResult');
    const btn = document.querySelector('#page-bots .bot-form button');
    
    if (!requirements) { showResult(resultDiv, '❌ Please enter bot requirements', 'error'); return; }
    
    btn.disabled = true;
    btn.textContent = '⏳ Creating...';
    resultDiv.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/create_bot`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ requirements, location, name: name || undefined })
        });
        const data = await response.json();
        if (data.status === 'success') {
            const bot = data.bot || {};
            showResult(resultDiv, `
✅ Bot created successfully!

🤖 Name: ${bot.name || 'Unnamed'}
📍 Location: ${bot.location || 'local'}
📝 Requirements: ${requirements}
            `, 'success');
            loadAllData();
            document.getElementById('botRequirements').value = '';
            document.getElementById('botName').value = '';
        } else {
            showResult(resultDiv, `❌ Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showResult(resultDiv, `❌ Error: ${error.message}`, 'error');
    }
    btn.disabled = false;
    btn.textContent = '🤖 Create Bot';
}

// ============================================
// 9. LOAD BOTS
// ============================================

async function loadBots() {
    try {
        const response = await fetch(`${API_BASE}/bots`);
        const data = await response.json();
        const container = document.getElementById('botsContainer');
        const bots = data.bots || [];
        if (bots.length === 0) {
            container.innerHTML = `<div class="empty-state"><span class="icon">🤖</span><p>No bots created yet</p></div>`;
            return;
        }
        let html = '';
        bots.slice().reverse().forEach(bot => {
            html += `
                <div class="bot-item">
                    <div class="bot-name">🤖 ${bot.name}</div>
                    <div class="bot-location">📌 ${bot.location || 'local'} | Status: ${bot.status || 'active'}</div>
                </div>
            `;
        });
        container.innerHTML = html;
    } catch (error) { console.error('Error loading bots:', error); }
}

// ============================================
// 10. LEARN
// ============================================

async function learnText() {
    const text = document.getElementById('learnText').value.trim();
    const category = document.getElementById('learnCategory').value;
    const source = document.getElementById('learnSource').value.trim();
    const resultDiv = document.getElementById('learnResult');
    const btn = document.querySelector('#page-learn .card:first-child button');
    
    if (!text) { showResult(resultDiv, '❌ Please enter text to learn', 'error'); return; }
    
    btn.disabled = true;
    btn.textContent = '⏳ Learning...';
    resultDiv.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/learn`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, category, source: source || 'user_input' })
        });
        const data = await response.json();
        if (data.status === 'success') {
            showResult(resultDiv, `
✅ Learning successful!

📚 Category: ${data.knowledge?.category || category}
📖 Source: ${data.knowledge?.source || source || 'user_input'}
📝 Learned: ${data.knowledge?.text || text.substring(0, 200) + '...'}
            `, 'success');
            loadAllData();
            document.getElementById('learnText').value = '';
            document.getElementById('learnSource').value = '';
        } else {
            showResult(resultDiv, `❌ Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showResult(resultDiv, `❌ Error: ${error.message}`, 'error');
    }
    btn.disabled = false;
    btn.textContent = '📚 Learn';
}

// ============================================
// 11. KNOWLEDGE
// ============================================

async function loadKnowledge() {
    try {
        const response = await fetch(`${API_BASE}/knowledge`);
        const data = await response.json();
        const container = document.getElementById('knowledgeContainer');
        if (data.status === 'success') {
            const items = data.knowledge || [];
            if (items.length === 0) {
                container.innerHTML = `<div class="empty-state"><span class="icon">📚</span><p>No knowledge yet. Teach the AI above!</p></div>`;
                return;
            }
            let html = `<div class="task-count">📚 ${items.length} knowledge items</div>`;
            items.slice().reverse().forEach(item => {
                html += `
                    <div class="knowledge-item">
                        <div class="knowledge-text">${item.text || 'No text'}</div>
                        <div class="knowledge-meta">${item.category || 'general'} | ${formatDate(item.learned)}</div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }
    } catch (error) { console.error('Error loading knowledge:', error); }
}

// ============================================
// 12. INTERNET FUNCTIONS
// ============================================

async function searchWeb() {
    const query = document.getElementById('searchInput')?.value;
    const resultDiv = document.getElementById('searchResult');
    if (!query) { showResult(resultDiv, '❌ Please enter a search query', 'error'); return; }
    
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '⏳ Searching the web...';
    
    try {
        const response = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, max_results: 10 })
        });
        const data = await response.json();
        if (data.status === 'success' && data.data?.results) {
            let html = `🔍 Search Results for: "${query}"\n\n`;
            data.data.results.forEach((r, i) => {
                html += `${i+1}. ${r.title || 'Untitled'}\n   ${r.snippet || 'No description'}\n   🔗 ${r.url}\n\n`;
            });
            showResult(resultDiv, html, 'success');
        } else {
            showResult(resultDiv, `❌ Search failed: ${data.data?.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        showResult(resultDiv, `❌ Error: ${error.message}`, 'error');
    }
}

async function fetchUrl() {
    const url = document.getElementById('urlInput')?.value;
    const resultDiv = document.getElementById('urlResult');
    if (!url) { showResult(resultDiv, '❌ Please enter a URL', 'error'); return; }
    
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '⏳ Fetching URL...';
    
    try {
        const response = await fetch(`${API_BASE}/fetch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, max_length: 5000 })
        });
        const data = await response.json();
        if (data.status === 'success' && data.data?.success) {
            const content = data.data.content || 'No content extracted';
            showResult(resultDiv, `📄 ${data.data.title || 'Untitled'}\n\n${content.substring(0, 2000)}...`, 'success');
        } else {
            showResult(resultDiv, `❌ Fetch failed: ${data.data?.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        showResult(resultDiv, `❌ Error: ${error.message}`, 'error');
    }
}

async function chatWithInternet() {
    const message = document.getElementById('chatInput')?.value;
    const useInternet = document.getElementById('chatInternet')?.checked || false;
    const resultDiv = document.getElementById('chatResult');
    if (!message) { showResult(resultDiv, '❌ Please enter a message', 'error'); return; }
    
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '⏳ Processing...';
    
    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, use_internet: useInternet })
        });
        const data = await response.json();
        if (data.status === 'success') {
            let responseText = data.chat?.response || 'No response';
            if (data.chat?.internet_results) {
                responseText += '\n\n🔍 Internet Results:\n';
                data.chat.internet_results.forEach((r, i) => {
                    responseText += `${i+1}. ${r.title || 'Untitled'}\n   ${r.snippet || ''}\n`;
                });
            }
            showResult(resultDiv, responseText, 'success');
        } else {
            showResult(resultDiv, `❌ Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showResult(resultDiv, `❌ Error: ${error.message}`, 'error');
    }
}

async function generateCode() {
    const description = document.getElementById('codeInput')?.value;
    const language = document.getElementById('codeLanguage')?.value || 'python';
    const framework = document.getElementById('codeFramework')?.value;
    const resultDiv = document.getElementById('codeResult');
    
    if (!description) { showResult(resultDiv, '❌ Please enter a code description', 'error'); return; }
    
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '⏳ Generating code...';
    
    try {
        const response = await fetch(`${API_BASE}/generate_code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ description, language, framework: framework || null })
        });
        const data = await response.json();
        if (data.status === 'success' && data.data?.success) {
            showResult(resultDiv, `💻 Generated ${language.toUpperCase()} Code\n\n${data.data.code}`, 'success');
        } else {
            showResult(resultDiv, `❌ Code generation failed: ${data.data?.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        showResult(resultDiv, `❌ Error: ${error.message}`, 'error');
    }
}

function showInternetTab(tab) {
    document.querySelectorAll('.internet-panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.internet-tabs .tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(`internet-${tab}`).classList.add('active');
    event.target.classList.add('active');
}

// ============================================
// 13. SYSTEM STATUS
// ============================================

async function loadSystemStatus() {
    try {
        const responses = await Promise.all([
            fetch(`${API_BASE}/health`),
            fetch(`${API_BASE}/version`),
            fetch(`${API_BASE}/metrics`)
        ]);
        const [health, version, metrics] = await Promise.all(responses.map(r => r.json()));
        const container = document.getElementById('systemStatus');
        container.innerHTML = `
            <div class="system-grid">
                <div><strong>Status:</strong> <span style="color:#00cc88;">${health.status || 'healthy'}</span></div>
                <div><strong>Version:</strong> ${version.version || APP_VERSION}</div>
                <div><strong>Deployment:</strong> ${version.deployment || 'Vercel'}</div>
                <div><strong>Uptime:</strong> ${formatUptime(version.uptime || 0)}</div>
                <div><strong>Tasks:</strong> ${metrics.tasks_total || 0}</div>
                <div><strong>Bots:</strong> ${metrics.bots_created || 0}</div>
                <div><strong>Knowledge:</strong> ${metrics.knowledge_items || 0}</div>
                <div><strong>Timestamp:</strong> ${new Date().toLocaleString()}</div>
            </div>
        `;
    } catch (error) { console.error('Error loading system status:', error); }
}

// ============================================
// 14. REFRESH & SETTINGS
// ============================================

function refreshData() {
    const btn = document.querySelector('.btn-refresh');
    btn.classList.add('spinning');
    loadAllData();
    setTimeout(() => btn.classList.remove('spinning'), 800);
}

function loadSettings() {
    const saved = localStorage.getItem('boijeluxSettings');
    if (saved) {
        settings = JSON.parse(saved);
        document.getElementById('refreshInterval').value = settings.refreshInterval || 30;
        document.getElementById('themeSelect').value = settings.theme || 'dark';
        applyTheme(settings.theme || 'dark');
    }
}

function saveSettings() {
    settings = {
        refreshInterval: parseInt(document.getElementById('refreshInterval').value) || 30,
        theme: document.getElementById('themeSelect').value
    };
    localStorage.setItem('boijeluxSettings', JSON.stringify(settings));
    applyTheme(settings.theme);
    setupAutoRefresh();
    showResult(document.getElementById('learnResult'), '✅ Settings saved successfully!', 'success');
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
}

function setupAutoRefresh() {
    if (refreshTimer) clearInterval(refreshTimer);
    const interval = (parseInt(document.getElementById('refreshInterval')?.value) || 30) * 1000;
    refreshTimer = setInterval(() => { if (!document.hidden) loadAllData(); }, interval);
}

// ============================================
// 15. KEYBOARD SHORTCUTS
// ============================================

function setupKeyboardShortcuts() {
    document.getElementById('quickTaskInput').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') { e.preventDefault(); processQuickTask(); }
    });
    document.getElementById('taskInput').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) { e.preventDefault(); processTask(); }
    });
    document.getElementById('learnText').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) { e.preventDefault(); learnText(); }
    });
    document.getElementById('searchInput').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') { e.preventDefault(); searchWeb(); }
    });
    document.getElementById('chatInput').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) { e.preventDefault(); chatWithInternet(); }
    });
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && e.key === 'R') {
            e.preventDefault();
            clearCacheAndRefresh();
        }
        if (e.ctrlKey && !e.shiftKey) {
            const pages = ['dashboard', 'tasks', 'bots', 'learn', 'internet', 'settings'];
            const idx = parseInt(e.key) - 1;
            if (idx >= 0 && idx < pages.length) {
                e.preventDefault();
                const link = document.querySelector(`.nav-link[data-page="${pages[idx]}"]`);
                if (link) link.click();
            }
        }
    });
}

// ============================================
// 16. CACHE MANAGEMENT
// ============================================

function clearCacheAndRefresh() {
    if (confirm('Clear all cache and refresh?')) {
        if ('caches' in window) caches.keys().then(keys => keys.forEach(key => caches.delete(key)));
        localStorage.clear();
        sessionStorage.clear();
        document.cookie.split(";").forEach(c => {
            document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
        });
        window.location.reload(true);
    }
}

function clearAllData() {
    if (confirm('⚠️ This will delete ALL data. Are you sure?')) {
        localStorage.clear();
        sessionStorage.clear();
        fetch(`${API_BASE}/clear`, { method: 'POST' }).catch(() => {});
        alert('✅ All data cleared!');
        window.location.reload();
    }
}

function exportData() {
    const data = { settings, version: APP_VERSION, timestamp: new Date().toISOString() };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `boijelux_data_${new Date().toISOString().slice(0,10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

function importData() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const data = JSON.parse(event.target.result);
                    if (data.settings) {
                        localStorage.setItem('boijeluxSettings', JSON.stringify(data.settings));
                        loadSettings();
                    }
                    alert('✅ Data imported successfully!');
                    window.location.reload();
                } catch (err) {
                    alert('❌ Invalid file format');
                }
            };
            reader.readAsText(file);
        }
    };
    input.click();
}

// ============================================
// 17. UTILITY FUNCTIONS
// ============================================

function showResult(container, message, type = 'success') {
    container.className = type;
    container.textContent = message;
    container.style.display = 'block';
}

function displayError(containerId, message) {
    document.getElementById(containerId).innerHTML = `<div class="error-state"><p>❌ ${message}</p></div>`;
}

function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    try { return new Date(dateStr).toLocaleString(); } catch { return dateStr; }
}

// ============================================
// 18. EXPOSE TO GLOBAL SCOPE
// ============================================

window.processTask = processTask;
window.processQuickTask = processQuickTask;
window.createBot = createBot;
window.learnText = learnText;
window.searchWeb = searchWeb;
window.fetchUrl = fetchUrl;
window.chatWithInternet = chatWithInternet;
window.generateCode = generateCode;
window.showInternetTab = showInternetTab;
window.refreshData = refreshData;
window.clearCacheAndRefresh = clearCacheAndRefresh;
window.clearAllData = clearAllData;
window.exportData = exportData;
window.importData = importData;
window.saveSettings = saveSettings;
window.toggleMobileNav = toggleMobileNav;

console.log(`🚀 Boijelux v${APP_VERSION} loaded`);
console.log('📌 Keyboard shortcuts:');
console.log('  Ctrl+1-6  - Navigate pages');
console.log('  Ctrl+Enter - Submit task');
console.log('  Ctrl+Shift+R - Clear cache and refresh');

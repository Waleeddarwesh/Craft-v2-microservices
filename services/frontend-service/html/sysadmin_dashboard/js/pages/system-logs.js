const SystemLogsPage = (() => {
    let allLogs = [];
    function render(container) {
        container.innerHTML = `
            <div class="page-header"><div><h2>${window.t('System Logs')}</h2><p class="text-secondary">${window.t('View and filter system log entries.')}</p></div></div>
            <div class="card"><div class="table-actions" style="display:flex;gap:var(--space-3);flex-wrap:wrap;align-items:center;">
                <div class="form-search" style="width:240px;"><svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input type="text" class="form-input" id="log-search" placeholder="${window.t('Search...')}" oninput="SystemLogsPage.filterData()"></div>
                <select class="form-input" id="log-level-filter" style="width:140px;" onchange="SystemLogsPage.filterData()">
                    <option value="">All Levels</option><option value="INFO">INFO</option><option value="WARN">WARN</option><option value="ERROR">ERROR</option><option value="CRITICAL">CRITICAL</option>
                </select>
                <select class="form-input" id="log-source-filter" style="width:160px;" onchange="SystemLogsPage.filterData()">
                    <option value="">All Sources</option>
                </select>
            </div>
                <div class="table-responsive"><table class="table" id="logs-table"><thead><tr><th>${window.t('Time')}</th><th>${window.t('Level')}</th><th>${window.t('Source')}</th><th>${window.t('Server')}</th><th>${window.t('Message')}</th></tr></thead>
                <tbody><tr><td colspan="5" class="text-center py-4"><div class="spinner"></div></td></tr></tbody></table></div></div>`;
        loadData();
    }
    async function loadData() {
        try {
            const data = await API.get('/api/system-admin/system-logs/');
            allLogs = Array.isArray(data) ? data : (data.results || []);
            // Populate source filter
            const sources = [...new Set(allLogs.map(l=>l.source))].sort();
            const srcSelect = document.getElementById('log-source-filter');
            if (srcSelect) { srcSelect.innerHTML = '<option value="">All Sources</option>' + sources.map(s=>`<option value="${s}">${s}</option>`).join(''); }
            renderTable(allLogs);
        } catch (e) { document.querySelector('#logs-table tbody').innerHTML = `<tr><td colspan="5" style="text-align:center;padding:32px;color:var(--clr-danger)">Failed: ${e.message}</td></tr>`; }
    }
    function renderTable(data) {
        const tbody = document.querySelector('#logs-table tbody');
        if (!data || data.length === 0) { tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:32px;color:var(--clr-text-muted)">No logs found.</td></tr>`; return; }
        // Sort by timestamp desc
        const sorted = [...data].sort((a,b) => new Date(b.timestamp) - new Date(a.timestamp));
        tbody.innerHTML = sorted.map(l => {
            const lvlClass = {INFO:'badge-info',WARN:'badge-warning',ERROR:'badge-danger',CRITICAL:'badge-danger'}[l.level]||'badge-neutral';
            return `<tr>
                <td style="font-size:var(--fs-sm);color:var(--clr-text-muted);white-space:nowrap;">${new Date(l.timestamp).toLocaleString()}</td>
                <td><span class="badge ${lvlClass}" style="${l.level==='CRITICAL'?'animation:pulse 2s infinite;':''}">${l.level}</span></td>
                <td><span class="badge badge-neutral">${l.source}</span></td>
                <td style="font-size:var(--fs-sm)">${l.server_hostname || (l.server ? 'Server #'+l.server : '-')}</td>
                <td style="font-family:var(--font-mono);font-size:var(--fs-xs);max-width:400px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${(l.message||'').replace(/"/g,'&quot;')}">${l.message}</td>
            </tr>`;
        }).join('');
    }
    function filterData() {
        const q = (document.getElementById('log-search')?.value||'').toLowerCase();
        const level = document.getElementById('log-level-filter')?.value || '';
        const source = document.getElementById('log-source-filter')?.value || '';
        let filtered = allLogs;
        if (q) filtered = filtered.filter(l => l.message.toLowerCase().includes(q) || l.source.toLowerCase().includes(q));
        if (level) filtered = filtered.filter(l => l.level === level);
        if (source) filtered = filtered.filter(l => l.source === source);
        renderTable(filtered);
    }
    return { render, loadData, filterData };
})();
window.SystemLogsPage = SystemLogsPage;

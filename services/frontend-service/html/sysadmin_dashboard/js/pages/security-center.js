const SecurityCenterPage = (() => {
    let serversList = [];

    async function loadData() {
        try {
            const [rules, alerts, contexts, servers] = await Promise.all([
                API.get('/api/system-admin/firewall-rules/'),
                API.get('/api/system-admin/security-alerts/'),
                API.get('/api/system-admin/selinux-contexts/'),
                API.get('/api/system-admin/servers/')
            ]);
            serversList = Array.isArray(servers) ? servers : (servers.results || []);
            renderFirewallRules(Array.isArray(rules) ? rules : (rules.results || []));
            renderSecurityAlerts(Array.isArray(alerts) ? alerts : (alerts.results || []));
            renderSELinuxContexts(Array.isArray(contexts) ? contexts : (contexts.results || []));
        } catch (error) { Toast.show('Failed to load security data: ' + error.message, 'error'); }
    }

    function renderFirewallRules(rules) {
        const tbody = document.getElementById('firewall-rules-tbody');
        if (!tbody) return;
        if (!rules.length) { tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:32px;color:var(--clr-text-muted)">No firewall rules found.</td></tr>`; return; }
        tbody.innerHTML = rules.map(r => `<tr>
            <td>${r.port} / ${r.protocol}</td>
            <td><span class="badge badge-${r.action==='allow'?'success':'danger'}">${r.action.toUpperCase()}</span></td>
            <td>${r.server_hostname || 'Server #'+r.server}</td>
            <td>${r.description || '-'}</td>
            <td style="display:flex;gap:4px;"><button class="btn btn-sm btn-outline" onclick="SecurityCenterPage.editRule(${r.id})">Edit</button><button class="btn btn-sm btn-outline" style="color:var(--clr-danger);border-color:var(--clr-danger)" onclick="SecurityCenterPage.deleteRule(${r.id})">Del</button></td>
        </tr>`).join('');
    }

    function renderSecurityAlerts(alerts) {
        const tbody = document.getElementById('security-alerts-tbody');
        if (!tbody) return;
        if (!alerts.length) { tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--clr-text-muted)">No security alerts.</td></tr>`; return; }
        tbody.innerHTML = alerts.map(a => {
            const sevClass = {critical:'badge-danger',high:'badge-warning',medium:'badge-info',low:'badge-neutral'}[a.severity]||'badge-neutral';
            return `<tr>
                <td style="font-size:var(--fs-sm)">${new Date(a.timestamp).toLocaleString()}</td>
                <td><strong>${a.title}</strong></td>
                <td><span class="badge ${sevClass}">${a.severity.toUpperCase()}</span></td>
                <td><span class="badge badge-${a.resolved?'success':'warning'}">${a.resolved?'Resolved':'Active'}</span></td>
                <td>${a.server_hostname || ''}</td>
                <td>${!a.resolved ? `<button class="btn btn-sm btn-outline" style="color:var(--clr-success);border-color:var(--clr-success)" onclick="SecurityCenterPage.resolveAlert(${a.id})">Resolve</button>` : ''}</td>
            </tr>`;
        }).join('');
    }

    function renderSELinuxContexts(contexts) {
        const tbody = document.getElementById('selinux-tbody');
        if (!tbody) return;
        if (!contexts.length) { tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:32px;color:var(--clr-text-muted)">No SELinux contexts.</td></tr>`; return; }
        tbody.innerHTML = contexts.map(c => `<tr>
            <td style="font-family:var(--font-mono);font-size:var(--fs-sm)">${c.file_path}</td>
            <td style="font-size:var(--fs-xs)">${c.expected_context}</td>
            <td style="font-size:var(--fs-xs)">${c.current_context}</td>
            <td><span class="badge badge-${c.status==='match'?'success':'danger'}">${c.status}</span></td>
            <td>${c.server_hostname || ''}</td>
        </tr>`).join('');
    }

    function getSeverityColor(severity) { return {critical:'danger',high:'warning',medium:'info',low:'neutral'}[severity]||'neutral'; }

    function render(container) {
        container.innerHTML = `
            <div class="page-header"><div><h2>${window.t('Security Center')}</h2><p class="text-secondary">${window.t('Firewall rules, security alerts, and SELinux contexts.')}</p></div>
                <div class="header-actions"><button class="btn btn-primary" onclick="SecurityCenterPage.openAddRuleModal()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> ${window.t('Add Firewall Rule')}</button></div></div>
            <h3 class="mt-4 mb-3">${window.t('Firewall Rules')}</h3>
            <div class="card mb-4"><div class="table-responsive"><table class="table"><thead><tr><th>${window.t('Port / Protocol')}</th><th>${window.t('Action')}</th><th>${window.t('Server')}</th><th>${window.t('Description')}</th><th>${window.t('Actions')}</th></tr></thead>
                <tbody id="firewall-rules-tbody"><tr><td colspan="5" class="text-center py-4"><div class="spinner"></div></td></tr></tbody></table></div></div>
            <h3 class="mb-3">${window.t('Security Alerts')}</h3>
            <div class="card mb-4"><div class="table-responsive"><table class="table"><thead><tr><th>${window.t('Time')}</th><th>${window.t('Alert')}</th><th>${window.t('Severity')}</th><th>${window.t('Status')}</th><th>${window.t('Server')}</th><th>${window.t('Actions')}</th></tr></thead>
                <tbody id="security-alerts-tbody"><tr><td colspan="6" class="text-center py-4"><div class="spinner"></div></td></tr></tbody></table></div></div>
            <h3 class="mb-3">${window.t('SELinux Contexts')}</h3>
            <div class="card"><div class="table-responsive"><table class="table"><thead><tr><th>${window.t('File Path')}</th><th>${window.t('Expected')}</th><th>${window.t('Current')}</th><th>${window.t('Status')}</th><th>${window.t('Server')}</th></tr></thead>
                <tbody id="selinux-tbody"><tr><td colspan="5" class="text-center py-4"><div class="spinner"></div></td></tr></tbody></table></div></div>`;
        loadData();
    }

    function _srvOpts(sel) { return serversList.map(s=>`<option value="${s.id}" ${s.id===sel?'selected':''}>${s.hostname}</option>`).join(''); }

    // Firewall CRUD
    function openAddRuleModal() {
        Modal.open(window.t('Add Firewall Rule'), `<div style="display:grid;gap:var(--space-4);">
            <div class="form-group"><label class="form-label">Server *</label><select class="form-input" id="fw-server">${_srvOpts()}</select></div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4);">
                <div class="form-group"><label class="form-label">Port *</label><input class="form-input" id="fw-port" placeholder="443"></div>
                <div class="form-group"><label class="form-label">Protocol</label><select class="form-input" id="fw-proto"><option value="tcp">TCP</option><option value="udp">UDP</option></select></div>
            </div>
            <div class="form-group"><label class="form-label">Action</label><select class="form-input" id="fw-action"><option value="allow">Allow</option><option value="deny">Deny</option></select></div>
            <div class="form-group"><label class="form-label">Description</label><input class="form-input" id="fw-desc" placeholder="HTTPS traffic"></div>
        </div>`, `<button class="btn btn-primary" onclick="SecurityCenterPage.submitRule()">Create</button>`);
    }
    async function submitRule() {
        const d = { server:parseInt(document.getElementById('fw-server').value), port:document.getElementById('fw-port').value.trim(), protocol:document.getElementById('fw-proto').value, action:document.getElementById('fw-action').value, description:document.getElementById('fw-desc').value.trim() };
        if (!d.port) return Toast.error('Port required.');
        try { await API.post('/api/system-admin/firewall-rules/', d); Toast.success('Firewall rule created!'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); }
    }
    async function editRule(id) {
        try {
            const r = await API.get('/api/system-admin/firewall-rules/'+id+'/');
            Modal.open(window.t('Edit Firewall Rule'), `<div style="display:grid;gap:var(--space-4);">
                <div class="form-group"><label class="form-label">Server</label><select class="form-input" id="fw-server">${_srvOpts(r.server)}</select></div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4);">
                    <div class="form-group"><label class="form-label">Port</label><input class="form-input" id="fw-port" value="${r.port}"></div>
                    <div class="form-group"><label class="form-label">Protocol</label><select class="form-input" id="fw-proto"><option value="tcp" ${r.protocol==='tcp'?'selected':''}>TCP</option><option value="udp" ${r.protocol==='udp'?'selected':''}>UDP</option></select></div>
                </div>
                <div class="form-group"><label class="form-label">Action</label><select class="form-input" id="fw-action"><option value="allow" ${r.action==='allow'?'selected':''}>Allow</option><option value="deny" ${r.action==='deny'?'selected':''}>Deny</option></select></div>
                <div class="form-group"><label class="form-label">Description</label><input class="form-input" id="fw-desc" value="${r.description||''}"></div>
            </div>`, `<button class="btn btn-primary" onclick="SecurityCenterPage.submitEditRule(${id})">Save</button>`);
        } catch(e) { Toast.error('Failed: '+e.message); }
    }
    async function submitEditRule(id) {
        const d = { server:parseInt(document.getElementById('fw-server').value), port:document.getElementById('fw-port').value.trim(), protocol:document.getElementById('fw-proto').value, action:document.getElementById('fw-action').value, description:document.getElementById('fw-desc').value.trim() };
        try { await API.patch('/api/system-admin/firewall-rules/'+id+'/', d); Toast.success('Updated!'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); }
    }
    async function deleteRule(id) { Modal.open(window.t('Delete'), `<p style="text-align:center;padding:16px;">Delete this firewall rule?</p>`, `<button class="btn btn-outline" onclick="Modal.close()">Cancel</button><button class="btn" style="background:var(--clr-danger);color:white" onclick="SecurityCenterPage.confirmDeleteRule(${id})">Delete</button>`); }
    async function confirmDeleteRule(id) { try { await API.delete('/api/system-admin/firewall-rules/'+id+'/'); Toast.success('Deleted.'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }

    // Resolve alert
    async function resolveAlert(id) { try { await API.post('/api/system-admin/security-alerts/'+id+'/resolve/'); Toast.success('Alert resolved!'); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }

    return { render, loadData, openAddRuleModal, submitRule, editRule, submitEditRule, deleteRule, confirmDeleteRule, resolveAlert };
})();
window.SecurityCenterPage = SecurityCenterPage;

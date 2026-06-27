const IncidentsPage = (() => {
    let allIncidents = [], serversList = [];
    function render(container) {
        container.innerHTML = `
            <div class="page-header"><div><h2>${window.t('Incident Management')}</h2><p class="text-secondary">${window.t('Track and resolve system incidents.')}</p></div>
                <div class="header-actions"><button class="btn btn-primary" onclick="IncidentsPage.openAddModal()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> ${window.t('Report Incident')}</button></div></div>
            <div class="card"><div class="table-actions"><div class="form-search" style="width:320px;"><svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input type="text" class="form-input" id="inc-search" placeholder="${window.t('Search...')}" oninput="IncidentsPage.filterData()"></div></div>
                <div class="table-responsive"><table class="table" id="inc-table"><thead><tr><th>${window.t('Title')}</th><th>${window.t('Server')}</th><th>${window.t('Severity')}</th><th>${window.t('Status')}</th><th>${window.t('Created')}</th><th>${window.t('Actions')}</th></tr></thead>
                <tbody><tr><td colspan="6" class="text-center py-4"><div class="spinner"></div></td></tr></tbody></table></div></div>`;
        loadData();
    }
    async function loadData() {
        try {
            const [inc, srv] = await Promise.all([API.get('/api/system-admin/incidents/'), API.get('/api/system-admin/servers/')]);
            allIncidents = Array.isArray(inc) ? inc : (inc.results || []);
            serversList = Array.isArray(srv) ? srv : (srv.results || []);
            renderTable(allIncidents);
        } catch (e) { document.querySelector('#inc-table tbody').innerHTML = `<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--clr-danger)">Failed: ${e.message}</td></tr>`; }
    }
    function renderTable(data) {
        const tbody = document.querySelector('#inc-table tbody');
        if (!data || data.length === 0) { tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--clr-text-muted)">No incidents found.</td></tr>`; return; }
        tbody.innerHTML = data.map(i => {
            const sevClass = {critical:'badge-danger',high:'badge-warning',medium:'badge-info',low:'badge-neutral'}[i.severity]||'badge-neutral';
            const statClass = {open:'badge-danger',investigating:'badge-warning',resolved:'badge-success',closed:'badge-neutral'}[i.status]||'badge-neutral';
            return `<tr>
                <td><div class="font-medium">${i.title}</div><div style="font-size:var(--fs-xs);color:var(--clr-text-muted);max-width:250px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${i.description||''}</div></td>
                <td>${i.server_hostname || (i.server ? 'Server #'+i.server : '-')}</td>
                <td><span class="badge ${sevClass}">${i.severity}</span></td>
                <td><span class="badge ${statClass}">${i.status}</span></td>
                <td style="font-size:var(--fs-sm);color:var(--clr-text-muted)">${i.created_at ? new Date(i.created_at).toLocaleDateString() : '-'}</td>
                <td style="display:flex;gap:4px;flex-wrap:wrap;">
                    ${i.status!=='resolved'&&i.status!=='closed' ? `<button class="btn btn-sm btn-outline" style="color:var(--clr-success);border-color:var(--clr-success)" onclick="IncidentsPage.resolveIncident(${i.id})">Resolve</button>` : ''}
                    <button class="btn btn-sm btn-outline" onclick="IncidentsPage.editIncident(${i.id})">Edit</button>
                    <button class="btn btn-sm btn-outline" style="color:var(--clr-danger);border-color:var(--clr-danger)" onclick="IncidentsPage.deleteIncident(${i.id})">Del</button>
                </td></tr>`;
        }).join('');
    }
    function filterData() { const q=(document.getElementById('inc-search')?.value||'').toLowerCase(); if(!q) return renderTable(allIncidents); renderTable(allIncidents.filter(i=>i.title.toLowerCase().includes(q)||(i.server_hostname||'').toLowerCase().includes(q)||i.severity.toLowerCase().includes(q)||i.status.toLowerCase().includes(q))); }
    function _srvOpts(sel) { return `<option value="">-- None --</option>` + serversList.map(s=>`<option value="${s.id}" ${s.id===sel?'selected':''}>${s.hostname}</option>`).join(''); }
    function _formHtml(d={}) { return `<div style="display:grid;gap:var(--space-4);">
        <div class="form-group"><label class="form-label">Title *</label><input class="form-input" id="inc-title" value="${d.title||''}" placeholder="High CPU Usage"></div>
        <div class="form-group"><label class="form-label">Description *</label><textarea class="form-input" id="inc-desc" rows="3" placeholder="Describe the incident...">${d.description||''}</textarea></div>
        <div class="form-group"><label class="form-label">Server</label><select class="form-input" id="inc-server">${_srvOpts(d.server)}</select></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4);">
            <div class="form-group"><label class="form-label">Severity *</label><select class="form-input" id="inc-sev"><option value="low" ${d.severity==='low'?'selected':''}>Low</option><option value="medium" ${d.severity==='medium'?'selected':''}>Medium</option><option value="high" ${d.severity==='high'?'selected':''}>High</option><option value="critical" ${d.severity==='critical'?'selected':''}>Critical</option></select></div>
            <div class="form-group"><label class="form-label">Status</label><select class="form-input" id="inc-stat"><option value="open" ${d.status==='open'?'selected':''}>Open</option><option value="investigating" ${d.status==='investigating'?'selected':''}>Investigating</option><option value="resolved" ${d.status==='resolved'?'selected':''}>Resolved</option><option value="closed" ${d.status==='closed'?'selected':''}>Closed</option></select></div>
        </div>
    </div>`; }
    function _getFormData() { const srv=document.getElementById('inc-server').value; return { title:document.getElementById('inc-title').value.trim(), description:document.getElementById('inc-desc').value.trim(), server:srv?parseInt(srv):null, severity:document.getElementById('inc-sev').value, status:document.getElementById('inc-stat').value }; }
    function openAddModal() { Modal.open(window.t('Report Incident'), _formHtml(), `<button class="btn btn-primary" onclick="IncidentsPage.submitAdd()">Create</button>`); }
    async function submitAdd() { const d=_getFormData(); if(!d.title||!d.description) return Toast.error('Title and description required.'); try { await API.post('/api/system-admin/incidents/',d); Toast.success('Incident reported!'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    async function editIncident(id) { const i=allIncidents.find(x=>x.id===id); if(!i) return; Modal.open(window.t('Edit Incident'), _formHtml(i), `<button class="btn btn-primary" onclick="IncidentsPage.submitEdit(${id})">Save</button>`); }
    async function submitEdit(id) { const d=_getFormData(); try { await API.patch('/api/system-admin/incidents/'+id+'/',d); Toast.success('Updated!'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    async function resolveIncident(id) { try { await API.patch('/api/system-admin/incidents/'+id+'/', {status:'resolved', resolved_at:new Date().toISOString()}); Toast.success('Incident resolved!'); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    async function deleteIncident(id) { Modal.open(window.t('Delete'), `<p style="text-align:center;padding:16px;">Delete this incident?</p>`, `<button class="btn btn-outline" onclick="Modal.close()">Cancel</button><button class="btn" style="background:var(--clr-danger);color:white" onclick="IncidentsPage.confirmDelete(${id})">Delete</button>`); }
    async function confirmDelete(id) { try { await API.delete('/api/system-admin/incidents/'+id+'/'); Toast.success('Deleted.'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    return { render, loadData, filterData, openAddModal, submitAdd, editIncident, submitEdit, resolveIncident, deleteIncident, confirmDelete };
})();
window.IncidentsPage = IncidentsPage;

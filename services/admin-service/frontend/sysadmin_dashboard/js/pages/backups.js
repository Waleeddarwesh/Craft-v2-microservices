const BackupsPage = (() => {
    let allBackups = [], serversList = [];
    function render(container) {
        container.innerHTML = `
            <div class="page-header"><div><h2>${window.t('Backup Management')}</h2><p class="text-secondary">${window.t('Schedule and monitor backup jobs.')}</p></div>
                <div class="header-actions"><button class="btn btn-primary" onclick="BackupsPage.openAddModal()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> ${window.t('Add Backup Job')}</button></div></div>
            <div class="card"><div class="table-actions"><div class="form-search" style="width:320px;"><svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input type="text" class="form-input" id="bk-search" placeholder="${window.t('Search...')}" oninput="BackupsPage.filterData()"></div></div>
                <div class="table-responsive"><table class="table" id="bk-table"><thead><tr><th>${window.t('Name')}</th><th>${window.t('Server')}</th><th>${window.t('Type')}</th><th>${window.t('Schedule')}</th><th>${window.t('Status')}</th><th>${window.t('Last Run')}</th><th>${window.t('Actions')}</th></tr></thead>
                <tbody><tr><td colspan="7" class="text-center py-4"><div class="spinner"></div></td></tr></tbody></table></div></div>`;
        loadData();
    }
    async function loadData() {
        try {
            const [bk, srv] = await Promise.all([API.get('/api/system-admin/backup-jobs/'), API.get('/api/system-admin/servers/')]);
            allBackups = Array.isArray(bk) ? bk : (bk.results || []);
            serversList = Array.isArray(srv) ? srv : (srv.results || []);
            renderTable(allBackups);
        } catch (e) { document.querySelector('#bk-table tbody').innerHTML = `<tr><td colspan="7" style="text-align:center;padding:32px;color:var(--clr-danger)">Failed: ${e.message}</td></tr>`; }
    }
    function renderTable(data) {
        const tbody = document.querySelector('#bk-table tbody');
        if (!data || data.length === 0) { tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:32px;color:var(--clr-text-muted)">No backup jobs found.</td></tr>`; return; }
        tbody.innerHTML = data.map(b => `<tr>
            <td class="font-medium">${b.name}</td>
            <td>${b.server_hostname || 'Server #'+b.server}</td>
            <td><span class="badge badge-neutral">${b.backup_type}</span></td>
            <td style="font-family:var(--font-mono);font-size:var(--fs-xs)">${b.schedule}</td>
            <td><span class="badge badge-${b.status==='active'?'success':'warning'}">${b.status}</span></td>
            <td style="font-size:var(--fs-sm);color:var(--clr-text-muted)">${b.last_run ? new Date(b.last_run).toLocaleString() : 'Never'}</td>
            <td style="display:flex;gap:4px;flex-wrap:wrap;">
                <button class="btn btn-sm btn-outline" style="color:var(--clr-success);border-color:var(--clr-success)" onclick="BackupsPage.runBackup(${b.id})">Run Now</button>
                <button class="btn btn-sm btn-outline" onclick="BackupsPage.editBackup(${b.id})">Edit</button>
                <button class="btn btn-sm btn-outline" style="color:var(--clr-danger);border-color:var(--clr-danger)" onclick="BackupsPage.deleteBackup(${b.id},'${b.name}')">Del</button>
            </td></tr>`).join('');
    }
    function filterData() { const q=(document.getElementById('bk-search')?.value||'').toLowerCase(); if(!q) return renderTable(allBackups); renderTable(allBackups.filter(b=>b.name.toLowerCase().includes(q)||(b.server_hostname||'').toLowerCase().includes(q)||(b.backup_type||'').toLowerCase().includes(q))); }
    function _srvOpts(sel) { return serversList.map(s=>`<option value="${s.id}" ${s.id===sel?'selected':''}>${s.hostname}</option>`).join(''); }
    function _formHtml(d={}) { return `<div style="display:grid;gap:var(--space-4);">
        <div class="form-group"><label class="form-label">Name *</label><input class="form-input" id="bk-name" value="${d.name||''}" placeholder="Daily DB Backup"></div>
        <div class="form-group"><label class="form-label">Server *</label><select class="form-input" id="bk-server">${_srvOpts(d.server)}</select></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4);">
            <div class="form-group"><label class="form-label">Type *</label><input class="form-input" id="bk-type" value="${d.backup_type||''}" placeholder="Database"></div>
            <div class="form-group"><label class="form-label">Schedule (cron) *</label><input class="form-input" id="bk-schedule" value="${d.schedule||''}" placeholder="0 1 * * *"></div>
        </div>
        <div class="form-group"><label class="form-label">Status</label><select class="form-input" id="bk-status"><option value="active" ${d.status==='active'?'selected':''}>Active</option><option value="disabled" ${d.status==='disabled'?'selected':''}>Disabled</option></select></div>
    </div>`; }
    function _getFormData() { return { name:document.getElementById('bk-name').value.trim(), server:parseInt(document.getElementById('bk-server').value), backup_type:document.getElementById('bk-type').value.trim(), schedule:document.getElementById('bk-schedule').value.trim(), status:document.getElementById('bk-status').value }; }
    function openAddModal() { Modal.open(window.t('Add Backup Job'), _formHtml(), `<button class="btn btn-primary" onclick="BackupsPage.submitAdd()">Create</button>`); }
    async function submitAdd() { const d=_getFormData(); if(!d.name||!d.backup_type) return Toast.error('Name and Type required.'); try { await API.post('/api/system-admin/backup-jobs/',d); Toast.success('Backup job created!'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    async function editBackup(id) { const b=allBackups.find(x=>x.id===id); if(!b) return; Modal.open(window.t('Edit Backup Job'), _formHtml(b), `<button class="btn btn-primary" onclick="BackupsPage.submitEdit(${id})">Save</button>`); }
    async function submitEdit(id) { const d=_getFormData(); try { await API.patch('/api/system-admin/backup-jobs/'+id+'/',d); Toast.success('Updated!'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    async function runBackup(id) { try { const res = await API.post('/api/system-admin/backup-jobs/'+id+'/run_backup/'); Toast.success(res.output || 'Backup completed!'); loadData(); } catch(e) { Toast.error('Backup failed: '+e.message); } }
    async function deleteBackup(id,name) { Modal.open(window.t('Delete'), `<div style="text-align:center;padding:16px;"><h3>Delete "${name}"?</h3></div>`, `<button class="btn btn-outline" onclick="Modal.close()">Cancel</button><button class="btn" style="background:var(--clr-danger);color:white" onclick="BackupsPage.confirmDelete(${id})">Delete</button>`); }
    async function confirmDelete(id) { try { await API.delete('/api/system-admin/backup-jobs/'+id+'/'); Toast.success('Deleted.'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    return { render, loadData, filterData, openAddModal, submitAdd, editBackup, submitEdit, runBackup, deleteBackup, confirmDelete };
})();
window.BackupsPage = BackupsPage;

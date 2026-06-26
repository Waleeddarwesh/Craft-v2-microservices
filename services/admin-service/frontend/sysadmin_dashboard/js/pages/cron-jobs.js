const CronJobsPage = (() => {
    let allCrons = [], serversList = [];
    function render(container) {
        container.innerHTML = `
            <div class="page-header"><div><h2>${window.t('Cron Jobs')}</h2><p class="text-secondary">${window.t('Schedule and manage recurring tasks.')}</p></div>
                <div class="header-actions"><button class="btn btn-primary" onclick="CronJobsPage.openAddModal()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> ${window.t('Add Cron Job')}</button></div></div>
            <div class="card"><div class="table-actions"><div class="form-search" style="width:320px;"><svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input type="text" class="form-input" id="cj-search" placeholder="${window.t('Search...')}" oninput="CronJobsPage.filterData()"></div></div>
                <div class="table-responsive"><table class="table" id="cj-table"><thead><tr><th>${window.t('Name')}</th><th>${window.t('Server')}</th><th>${window.t('Schedule')}</th><th>${window.t('Command')}</th><th>${window.t('User')}</th><th>${window.t('Status')}</th><th>${window.t('Actions')}</th></tr></thead>
                <tbody><tr><td colspan="7" class="text-center py-4"><div class="spinner"></div></td></tr></tbody></table></div></div>`;
        loadData();
    }
    async function loadData() {
        try {
            const [cj, srv] = await Promise.all([API.get('/api/system-admin/cron-jobs/'), API.get('/api/system-admin/servers/')]);
            allCrons = Array.isArray(cj) ? cj : (cj.results || []);
            serversList = Array.isArray(srv) ? srv : (srv.results || []);
            renderTable(allCrons);
        } catch (e) { document.querySelector('#cj-table tbody').innerHTML = `<tr><td colspan="7" style="text-align:center;padding:32px;color:var(--clr-danger)">Failed: ${e.message}</td></tr>`; }
    }
    function renderTable(data) {
        const tbody = document.querySelector('#cj-table tbody');
        if (!data || data.length === 0) { tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:32px;color:var(--clr-text-muted)">No cron jobs found.</td></tr>`; return; }
        tbody.innerHTML = data.map(c => `<tr>
            <td class="font-medium">${c.name}</td>
            <td>${c.server_hostname || 'Server #'+c.server}</td>
            <td style="font-family:var(--font-mono);font-size:var(--fs-xs)">${c.schedule}</td>
            <td style="font-family:var(--font-mono);font-size:var(--fs-xs);max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${c.command}">${c.command}</td>
            <td><span class="badge badge-neutral">${c.user}</span></td>
            <td><span class="badge badge-${c.status==='active'?'success':'warning'}">${c.status}</span></td>
            <td style="display:flex;gap:4px;flex-wrap:wrap;">
                <button class="btn btn-sm btn-outline" onclick="CronJobsPage.toggleStatus(${c.id},'${c.status}')">${c.status==='active'?'Disable':'Enable'}</button>
                <button class="btn btn-sm btn-outline" onclick="CronJobsPage.editCron(${c.id})">Edit</button>
                <button class="btn btn-sm btn-outline" style="color:var(--clr-danger);border-color:var(--clr-danger)" onclick="CronJobsPage.deleteCron(${c.id},'${c.name}')">Del</button>
            </td></tr>`).join('');
    }
    function filterData() { const q=(document.getElementById('cj-search')?.value||'').toLowerCase(); if(!q) return renderTable(allCrons); renderTable(allCrons.filter(c=>c.name.toLowerCase().includes(q)||(c.server_hostname||'').toLowerCase().includes(q)||c.command.toLowerCase().includes(q))); }
    function _srvOpts(sel) { return serversList.map(s=>`<option value="${s.id}" ${s.id===sel?'selected':''}>${s.hostname}</option>`).join(''); }
    function _formHtml(d={}) { return `<div style="display:grid;gap:var(--space-4);">
        <div class="form-group"><label class="form-label">Name *</label><input class="form-input" id="cj-name" value="${d.name||''}" placeholder="Log Rotation"></div>
        <div class="form-group"><label class="form-label">Server *</label><select class="form-input" id="cj-server">${_srvOpts(d.server)}</select></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4);">
            <div class="form-group"><label class="form-label">Schedule (cron) *</label><input class="form-input" id="cj-schedule" value="${d.schedule||''}" placeholder="0 0 * * *"></div>
            <div class="form-group"><label class="form-label">User</label><input class="form-input" id="cj-user" value="${d.user||'root'}" placeholder="root"></div>
        </div>
        <div class="form-group"><label class="form-label">Command *</label><textarea class="form-input" id="cj-cmd" rows="3" placeholder="/usr/sbin/logrotate -f /etc/logrotate.conf">${d.command||''}</textarea></div>
        <div class="form-group"><label class="form-label">Status</label><select class="form-input" id="cj-status"><option value="active" ${d.status==='active'?'selected':''}>Active</option><option value="disabled" ${d.status==='disabled'?'selected':''}>Disabled</option></select></div>
    </div>`; }
    function _getFormData() { return { name:document.getElementById('cj-name').value.trim(), server:parseInt(document.getElementById('cj-server').value), schedule:document.getElementById('cj-schedule').value.trim(), user:document.getElementById('cj-user').value.trim()||'root', command:document.getElementById('cj-cmd').value.trim(), status:document.getElementById('cj-status').value }; }
    function openAddModal() { Modal.open(window.t('Add Cron Job'), _formHtml(), `<button class="btn btn-primary" onclick="CronJobsPage.submitAdd()">Create</button>`); }
    async function submitAdd() { const d=_getFormData(); if(!d.name||!d.schedule||!d.command) return Toast.error('Name, schedule and command required.'); try { await API.post('/api/system-admin/cron-jobs/',d); Toast.success('Cron job created!'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    async function editCron(id) { const c=allCrons.find(x=>x.id===id); if(!c) return; Modal.open(window.t('Edit Cron Job'), _formHtml(c), `<button class="btn btn-primary" onclick="CronJobsPage.submitEdit(${id})">Save</button>`); }
    async function submitEdit(id) { const d=_getFormData(); try { await API.patch('/api/system-admin/cron-jobs/'+id+'/',d); Toast.success('Updated!'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    async function toggleStatus(id, current) { try { await API.patch('/api/system-admin/cron-jobs/'+id+'/', {status: current==='active'?'disabled':'active'}); Toast.success('Status toggled!'); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    async function deleteCron(id,name) { Modal.open(window.t('Delete'), `<div style="text-align:center;padding:16px;"><h3>Delete "${name}"?</h3></div>`, `<button class="btn btn-outline" onclick="Modal.close()">Cancel</button><button class="btn" style="background:var(--clr-danger);color:white" onclick="CronJobsPage.confirmDelete(${id})">Delete</button>`); }
    async function confirmDelete(id) { try { await API.delete('/api/system-admin/cron-jobs/'+id+'/'); Toast.success('Deleted.'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    return { render, loadData, filterData, openAddModal, submitAdd, editCron, submitEdit, toggleStatus, deleteCron, confirmDelete };
})();
window.CronJobsPage = CronJobsPage;

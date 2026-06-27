const UsersLinuxPage = (() => {
    let allUsers = [], serversList = [];
    function render(container) {
        container.innerHTML = `
            <div class="page-header"><div><h2>${window.t('Linux Users')}</h2><p class="text-secondary">${window.t('Manage system user accounts and sudo access.')}</p></div>
                <div class="header-actions"><button class="btn btn-primary" onclick="UsersLinuxPage.openAddModal()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> ${window.t('Add User')}</button></div></div>
            <div class="card"><div class="table-actions"><div class="form-search" style="width:320px;"><svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input type="text" class="form-input" id="lu-search" placeholder="${window.t('Search...')}" oninput="UsersLinuxPage.filterData()"></div></div>
                <div class="table-responsive"><table class="table" id="lu-table"><thead><tr><th>${window.t('Username')}</th><th>${window.t('Server')}</th><th>${window.t('Group')}</th><th>${window.t('Sudo')}</th><th>${window.t('Status')}</th><th>${window.t('Actions')}</th></tr></thead>
                <tbody><tr><td colspan="6" class="text-center py-4"><div class="spinner"></div></td></tr></tbody></table></div></div>`;
        loadData();
    }
    async function loadData() {
        try {
            const [users, servers] = await Promise.all([API.get('/api/system-admin/linux-users/'), API.get('/api/system-admin/servers/')]);
            allUsers = Array.isArray(users) ? users : (users.results || []);
            serversList = Array.isArray(servers) ? servers : (servers.results || []);
            renderTable(allUsers);
        } catch (e) { document.querySelector('#lu-table tbody').innerHTML = `<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--clr-danger)">Failed: ${e.message}</td></tr>`; }
    }
    function renderTable(data) {
        const tbody = document.querySelector('#lu-table tbody');
        if (!data || data.length === 0) { tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--clr-text-muted)">No users found.</td></tr>`; return; }
        tbody.innerHTML = data.map(u => `<tr>
            <td class="font-medium">${u.username}</td>
            <td>${u.server_hostname || 'Server #'+u.server}</td>
            <td><span class="badge badge-neutral">${u.group}</span></td>
            <td>${u.sudo_access ? '<span class="badge badge-warning">Yes</span>' : '<span class="badge badge-neutral">No</span>'}</td>
            <td><span class="badge badge-${u.status==='active'?'success':'danger'}">${u.status}</span></td>
            <td style="display:flex;gap:4px;"><button class="btn btn-sm btn-outline" onclick="UsersLinuxPage.editUser(${u.id})">Edit</button><button class="btn btn-sm btn-outline" style="color:var(--clr-danger);border-color:var(--clr-danger)" onclick="UsersLinuxPage.deleteUser(${u.id},'${u.username}')">Del</button></td>
        </tr>`).join('');
    }
    function filterData() { const q=(document.getElementById('lu-search')?.value||'').toLowerCase(); if(!q) return renderTable(allUsers); renderTable(allUsers.filter(u=>u.username.toLowerCase().includes(q)||(u.server_hostname||'').toLowerCase().includes(q)||u.group.toLowerCase().includes(q))); }
    function _srvOpts(sel) { return serversList.map(s=>`<option value="${s.id}" ${s.id===sel?'selected':''}>${s.hostname}</option>`).join(''); }
    function _formHtml(d={}) { return `<div style="display:grid;gap:var(--space-4);">
        <div class="form-group"><label class="form-label">Server *</label><select class="form-input" id="lu-server">${_srvOpts(d.server)}</select></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4);">
            <div class="form-group"><label class="form-label">Username *</label><input class="form-input" id="lu-user" value="${d.username||''}" placeholder="deploy"></div>
            <div class="form-group"><label class="form-label">Group *</label><input class="form-input" id="lu-group" value="${d.group||''}" placeholder="www-data"></div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4);">
            <div class="form-group"><label class="form-label">Sudo Access</label><select class="form-input" id="lu-sudo"><option value="true" ${d.sudo_access?'selected':''}>Yes</option><option value="false" ${!d.sudo_access?'selected':''}>No</option></select></div>
            <div class="form-group"><label class="form-label">Status</label><select class="form-input" id="lu-status"><option value="active" ${d.status==='active'?'selected':''}>Active</option><option value="disabled" ${d.status==='disabled'?'selected':''}>Disabled</option></select></div>
        </div>
    </div>`; }
    function _getFormData() { return { server:parseInt(document.getElementById('lu-server').value), username:document.getElementById('lu-user').value.trim(), group:document.getElementById('lu-group').value.trim(), sudo_access:document.getElementById('lu-sudo').value==='true', status:document.getElementById('lu-status').value }; }
    function openAddModal() { Modal.open(window.t('Add Linux User'), _formHtml(), `<button class="btn btn-primary" onclick="UsersLinuxPage.submitAdd()">Create</button>`); }
    async function submitAdd() { const d=_getFormData(); if(!d.username||!d.group) return Toast.error('Username and Group required.'); try { await API.post('/api/system-admin/linux-users/',d); Toast.success('User created!'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    async function editUser(id) { const u=allUsers.find(x=>x.id===id); if(!u) return; Modal.open(window.t('Edit User'), _formHtml(u), `<button class="btn btn-primary" onclick="UsersLinuxPage.submitEdit(${id})">Save</button>`); }
    async function submitEdit(id) { const d=_getFormData(); try { await API.patch('/api/system-admin/linux-users/'+id+'/',d); Toast.success('Updated!'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    async function deleteUser(id,name) { Modal.open(window.t('Delete User'), `<div style="text-align:center;padding:16px;"><h3>Delete user "${name}"?</h3><p style="color:var(--clr-text-muted)">This cannot be undone.</p></div>`, `<button class="btn btn-outline" onclick="Modal.close()">Cancel</button><button class="btn" style="background:var(--clr-danger);color:white" onclick="UsersLinuxPage.confirmDelete(${id})">Delete</button>`); }
    async function confirmDelete(id) { try { await API.delete('/api/system-admin/linux-users/'+id+'/'); Toast.success('Deleted.'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    return { render, loadData, filterData, openAddModal, submitAdd, editUser, submitEdit, deleteUser, confirmDelete };
})();
window.UsersLinuxPage = UsersLinuxPage;

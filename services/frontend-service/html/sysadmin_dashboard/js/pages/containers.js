const ContainersPage = (() => {
    let allContainers = [], serversList = [];
    function render(container) {
        container.innerHTML = `
            <div class="page-header"><div><h2>${window.t('Container Operations')}</h2><p class="text-secondary">${window.t('Administer Docker/Podman containers and OpenShift/Kubernetes.')}</p></div>
                <div class="header-actions"><button class="btn btn-primary" onclick="ContainersPage.openAddModal()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> ${window.t('Add New')}</button></div></div>
            <div class="card"><div class="table-actions"><div class="form-search" style="width:320px;"><svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input type="text" class="form-input" id="ct-search" placeholder="${window.t('Search containers...')}" oninput="ContainersPage.filterData()"></div></div>
                <div class="table-responsive"><table class="table" id="ct-table"><thead><tr><th>${window.t('Name')}</th><th>${window.t('Image')}</th><th>${window.t('State')}</th><th>${window.t('Ports')}</th><th>${window.t('Actions')}</th></tr></thead>
                <tbody><tr><td colspan="5" class="text-center py-4"><div class="spinner"></div></td></tr></tbody></table></div></div>`;
        loadData();
    }
    async function loadData() {
        try {
            const [ctData, srvData] = await Promise.all([API.get('/api/system-admin/containers/'), API.get('/api/system-admin/servers/')]);
            allContainers = Array.isArray(ctData) ? ctData : (ctData.results || []);
            serversList = Array.isArray(srvData) ? srvData : (srvData.results || []);
            renderTable(allContainers);
        } catch (e) { document.querySelector('#ct-table tbody').innerHTML = `<tr><td colspan="5" style="text-align:center;padding:32px;color:var(--clr-danger)">Failed: ${e.message}</td></tr>`; }
    }
    function renderTable(data) {
        const tbody = document.querySelector('#ct-table tbody');
        if (!data || data.length === 0) { tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:32px;color:var(--clr-text-muted)">No containers found.</td></tr>`; return; }
        tbody.innerHTML = data.map(c => {
            const stateClass = c.state === 'running' ? 'badge-success' : c.state === 'exited' ? 'badge-danger' : 'badge-warning';
            return `<tr>
                <td><div class="font-medium">${c.name}</div><div style="font-family:var(--font-mono);font-size:var(--fs-xs);color:var(--clr-text-muted)">${(c.container_id||'').substring(0,12)}</div></td>
                <td style="font-family:var(--font-mono);font-size:var(--fs-sm)">${c.image}</td>
                <td><span class="badge ${stateClass}">${c.state}</span><div style="font-size:var(--fs-xs);color:var(--clr-text-muted)">${c.status||''}</div></td>
                <td style="font-family:var(--font-mono);font-size:var(--fs-xs)">${c.ports || '-'}</td>
                <td style="display:flex;gap:4px;flex-wrap:wrap;">
                    <button class="btn btn-sm btn-outline" onclick="ContainersPage.editContainer(${c.id})">Edit</button>
                    <button class="btn btn-sm btn-outline" style="color:var(--clr-danger);border-color:var(--clr-danger)" onclick="ContainersPage.deleteContainer(${c.id},'${c.name}')">Del</button>
                </td></tr>`;
        }).join('');
    }
    function filterData() { const q=(document.getElementById('ct-search')?.value||'').toLowerCase(); if(!q) return renderTable(allContainers); renderTable(allContainers.filter(c=>c.name.toLowerCase().includes(q)||c.image.toLowerCase().includes(q)||(c.state||'').toLowerCase().includes(q))); }
    function _formHtml(d={}) {
        const srvOpts = serversList.map(s=>`<option value="${s.id}" ${s.id===d.server?'selected':''}>${s.hostname}</option>`).join('');
        return `<div style="display:grid;gap:var(--space-4);">
            <div class="form-group"><label class="form-label">Name *</label><input class="form-input" id="ct-name" value="${d.name||''}" placeholder="my-container"></div>
            <div class="form-group"><label class="form-label">Image *</label><input class="form-input" id="ct-image" value="${d.image||''}" placeholder="nginx:latest"></div>
            <div class="form-group"><label class="form-label">Container ID</label><input class="form-input" id="ct-cid" value="${d.container_id||''}" placeholder="abc123..."></div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4);">
                <div class="form-group"><label class="form-label">Server</label><select class="form-input" id="ct-server"><option value="">-- None --</option>${srvOpts}</select></div>
                <div class="form-group"><label class="form-label">State</label><select class="form-input" id="ct-state"><option value="running" ${d.state==='running'?'selected':''}>Running</option><option value="exited" ${d.state==='exited'?'selected':''}>Exited</option><option value="paused" ${d.state==='paused'?'selected':''}>Paused</option></select></div>
            </div>
            <div class="form-group"><label class="form-label">Ports</label><input class="form-input" id="ct-ports" value="${d.ports||''}" placeholder="0.0.0.0:8080->80/tcp"></div>
        </div>`;
    }
    function _getFormData() { return { name:document.getElementById('ct-name').value.trim(), image:document.getElementById('ct-image').value.trim(), container_id:document.getElementById('ct-cid').value.trim()||('auto_'+Date.now()), server:document.getElementById('ct-server').value?parseInt(document.getElementById('ct-server').value):null, state:document.getElementById('ct-state').value, status:document.getElementById('ct-state').value==='running'?'Up':'Exited', ports:document.getElementById('ct-ports').value.trim() }; }
    function openAddModal() { Modal.open(window.t('Add Container'), _formHtml(), `<button class="btn btn-primary" onclick="ContainersPage.submitAdd()">Create</button>`); }
    async function submitAdd() { const d=_getFormData(); if(!d.name||!d.image) return Toast.error('Name and Image are required.'); try { await API.post('/api/system-admin/containers/',d); Toast.success('Container created!'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    async function editContainer(id) { const c=allContainers.find(x=>x.id===id); if(!c) return; Modal.open(window.t('Edit Container'), _formHtml(c), `<button class="btn btn-primary" onclick="ContainersPage.submitEdit(${id})">Save</button>`); }
    async function submitEdit(id) { const d=_getFormData(); try { await API.patch('/api/system-admin/containers/'+id+'/',d); Toast.success('Container updated!'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    async function deleteContainer(id,name) { Modal.open(window.t('Delete Container'), `<div style="text-align:center;padding:16px;"><h3>Delete "${name}"?</h3><p style="color:var(--clr-text-muted)">This cannot be undone.</p></div>`, `<button class="btn btn-outline" onclick="Modal.close()">Cancel</button><button class="btn" style="background:var(--clr-danger);color:white" onclick="ContainersPage.confirmDelete(${id})">Delete</button>`); }
    async function confirmDelete(id) { try { await API.delete('/api/system-admin/containers/'+id+'/'); Toast.success('Container deleted.'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    return { render, loadData, filterData, openAddModal, submitAdd, editContainer, submitEdit, deleteContainer, confirmDelete };
})();
window.ContainersPage = ContainersPage;

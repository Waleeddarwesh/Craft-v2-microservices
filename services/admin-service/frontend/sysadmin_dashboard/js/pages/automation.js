const AutomationPage = (() => {
    let allScripts = [];
    function render(container) {
        container.innerHTML = `
            <div class="page-header"><div><h2>${window.t('Operational Scripts')}</h2><p class="text-secondary">${window.t('Store, schedule, and execute automation scripts.')}</p></div>
                <div class="header-actions"><button class="btn btn-primary" onclick="AutomationPage.openAddModal()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> ${window.t('New Script')}</button></div></div>
            <div class="card"><div class="table-actions"><div class="form-search" style="width:320px;"><svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input type="text" class="form-input" id="sc-search" placeholder="${window.t('Search...')}" oninput="AutomationPage.filterData()"></div></div>
                <div class="table-responsive"><table class="table" id="scripts-table"><thead><tr><th>${window.t('Name')}</th><th>${window.t('Description')}</th><th>${window.t('Interpreter')}</th><th>${window.t('Created')}</th><th>${window.t('Actions')}</th></tr></thead>
                <tbody><tr><td colspan="5" class="text-center py-4"><div class="spinner"></div></td></tr></tbody></table></div></div>`;
        loadData();
    }
    async function loadData() {
        try {
            const data = await API.get('/api/system-admin/scripts/');
            allScripts = Array.isArray(data) ? data : (data.results || []);
            renderTable(allScripts);
        } catch (e) { document.querySelector('#scripts-table tbody').innerHTML = `<tr><td colspan="5" style="text-align:center;padding:32px;color:var(--clr-danger)">Failed: ${e.message}</td></tr>`; }
    }
    function renderTable(data) {
        const tbody = document.querySelector('#scripts-table tbody');
        if (!data || data.length === 0) { tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:32px;color:var(--clr-text-muted)">No scripts found.</td></tr>`; return; }
        tbody.innerHTML = data.map(s => `<tr>
            <td class="font-medium" style="font-family:var(--font-mono)">${s.name}</td>
            <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--clr-text-muted);font-size:var(--fs-sm)">${s.description||'-'}</td>
            <td><span class="badge badge-neutral">${s.interpreter}</span></td>
            <td style="font-size:var(--fs-sm);color:var(--clr-text-muted)">${s.created_at ? new Date(s.created_at).toLocaleDateString() : '-'}</td>
            <td style="display:flex;gap:4px;flex-wrap:wrap;">
                <button class="btn btn-sm btn-outline" onclick="AutomationPage.viewScript(${s.id})">View</button>
                <button class="btn btn-sm btn-outline" style="color:var(--clr-success);border-color:var(--clr-success)" onclick="AutomationPage.executeScript(${s.id})">Run</button>
                <button class="btn btn-sm btn-outline" onclick="AutomationPage.editScript(${s.id})">Edit</button>
                <button class="btn btn-sm btn-outline" style="color:var(--clr-danger);border-color:var(--clr-danger)" onclick="AutomationPage.deleteScript(${s.id},'${s.name}')">Del</button>
            </td></tr>`).join('');
    }
    function filterData() { const q=(document.getElementById('sc-search')?.value||'').toLowerCase(); if(!q) return renderTable(allScripts); renderTable(allScripts.filter(s=>s.name.toLowerCase().includes(q)||(s.description||'').toLowerCase().includes(q))); }

    function _formHtml(d={}) { return `<div style="display:grid;gap:var(--space-4);">
        <div class="form-group"><label class="form-label">Name *</label><input class="form-input" id="sc-name" value="${d.name||''}" placeholder="deploy_app.sh"></div>
        <div class="form-group"><label class="form-label">Description</label><input class="form-input" id="sc-desc" value="${d.description||''}" placeholder="Automated deployment script"></div>
        <div class="form-group"><label class="form-label">Interpreter</label><select class="form-input" id="sc-interp">
            <option value="/bin/bash" ${d.interpreter==='/bin/bash'?'selected':''}>/bin/bash</option>
            <option value="/usr/bin/python3" ${d.interpreter==='/usr/bin/python3'?'selected':''}>/usr/bin/python3</option>
            <option value="/usr/bin/env node" ${d.interpreter==='/usr/bin/env node'?'selected':''}>/usr/bin/env node</option>
        </select></div>
        <div class="form-group"><label class="form-label">Script Content *</label><textarea class="form-input" id="sc-content" rows="10" style="font-family:var(--font-mono);font-size:var(--fs-sm);tab-size:4;" placeholder="#!/bin/bash&#10;echo 'Hello World'">${d.script_content||''}</textarea></div>
    </div>`; }
    function _getFormData() { return { name:document.getElementById('sc-name').value.trim(), description:document.getElementById('sc-desc').value.trim(), interpreter:document.getElementById('sc-interp').value, script_content:document.getElementById('sc-content').value }; }

    function openAddModal() { Modal.open(window.t('New Script'), _formHtml(), `<button class="btn btn-primary" onclick="AutomationPage.submitAdd()">Create</button>`); }
    async function submitAdd() { const d=_getFormData(); if(!d.name||!d.script_content) return Toast.error('Name and content required.'); try { await API.post('/api/system-admin/scripts/',d); Toast.success('Script created!'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }

    async function editScript(id) { const s=allScripts.find(x=>x.id===id); if(!s) return; Modal.open(window.t('Edit Script'), _formHtml(s), `<button class="btn btn-primary" onclick="AutomationPage.submitEdit(${id})">Save</button>`); }
    async function submitEdit(id) { const d=_getFormData(); try { await API.patch('/api/system-admin/scripts/'+id+'/',d); Toast.success('Updated!'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }

    async function viewScript(id) {
        const s = allScripts.find(x=>x.id===id);
        if (!s) return;
        Modal.open(s.name, `<div style="padding:4px;">
            <div style="margin-bottom:12px;"><span class="badge badge-neutral">${s.interpreter}</span> <span style="color:var(--clr-text-muted);font-size:var(--fs-sm);margin-left:8px;">${s.description||''}</span></div>
            <pre style="background:var(--clr-bg);border:1px solid var(--clr-border);border-radius:8px;padding:16px;overflow-x:auto;font-size:var(--fs-sm);font-family:var(--font-mono);max-height:400px;overflow-y:auto;">${(s.script_content||'').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</pre>
        </div>`, `<button class="btn btn-outline" onclick="Modal.close()">Close</button><button class="btn btn-primary" onclick="AutomationPage.executeScript(${id})">Execute</button>`);
    }

    async function executeScript(id) {
        try {
            const res = await API.post('/api/system-admin/scripts/'+id+'/execute/');
            Modal.open(window.t('Execution Result'), `<div style="padding:8px;">
                <div style="margin-bottom:12px;"><span class="badge badge-${res.success?'success':'danger'}">${res.success?'Success':'Failed'}</span></div>
                <pre style="background:var(--clr-bg);border:1px solid var(--clr-border);border-radius:8px;padding:16px;font-family:var(--font-mono);font-size:var(--fs-sm);white-space:pre-wrap;">${res.output||'No output.'}</pre>
            </div>`, `<button class="btn btn-outline" onclick="Modal.close()">Close</button>`);
        } catch(e) { Toast.error('Execution failed: '+e.message); }
    }

    async function deleteScript(id,name) { Modal.open(window.t('Delete'), `<div style="text-align:center;padding:16px;"><h3>Delete "${name}"?</h3></div>`, `<button class="btn btn-outline" onclick="Modal.close()">Cancel</button><button class="btn" style="background:var(--clr-danger);color:white" onclick="AutomationPage.confirmDelete(${id})">Delete</button>`); }
    async function confirmDelete(id) { try { await API.delete('/api/system-admin/scripts/'+id+'/'); Toast.success('Deleted.'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }

    return { render, loadData, filterData, openAddModal, submitAdd, editScript, submitEdit, viewScript, executeScript, deleteScript, confirmDelete };
})();
window.AutomationPage = AutomationPage;

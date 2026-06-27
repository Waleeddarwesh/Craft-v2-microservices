const ServicesPage = (() => {
    let allServices = [], serversList = [];

    function render(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h2>${window.t('Services Registry')}</h2>
                    <p class="text-secondary">${window.t('Manage all system services from one place.')}</p>
                </div>
                <div class="header-actions">
                    <button class="btn btn-primary" onclick="ServicesPage.openAddModal()">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                        ${window.t('Add New')}
                    </button>
                </div>
            </div>
            <div class="card">
                <div class="table-actions">
                    <div class="form-search" style="width:320px;max-width:100%;"><svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                        <input type="text" class="form-input" id="svc-search" placeholder="${window.t('Search...')}" oninput="ServicesPage.filterData()">
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table" id="services-table">
                        <thead><tr><th>${window.t('Name')}</th><th>${window.t('Server')}</th><th>${window.t('Type')}</th><th>${window.t('Status')}</th><th>${window.t('Last Restart')}</th><th>${window.t('Actions')}</th></tr></thead>
                        <tbody><tr><td colspan="6" class="text-center py-4"><div class="spinner"></div></td></tr></tbody>
                    </table>
                </div>
            </div>`;
        loadData();
    }

    async function loadData() {
        try {
            const [svcData, srvData] = await Promise.all([
                API.get('/api/system-admin/services/'),
                API.get('/api/system-admin/servers/')
            ]);
            allServices = Array.isArray(svcData) ? svcData : (svcData.results || []);
            serversList = Array.isArray(srvData) ? srvData : (srvData.results || []);
            renderTable(allServices);
        } catch (e) {
            document.querySelector('#services-table tbody').innerHTML = `<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--clr-danger)">Failed: ${e.message}</td></tr>`;
        }
    }

    function renderTable(data) {
        const tbody = document.querySelector('#services-table tbody');
        if (!data || data.length === 0) { tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--clr-text-muted)">No services found.</td></tr>`; return; }
        tbody.innerHTML = data.map(s => {
            const statusBadge = s.status === 'running' ? 'badge-success' : s.status === 'stopped' ? 'badge-danger' : 'badge-warning';
            const restart = s.last_restart ? new Date(s.last_restart).toLocaleString() : '-';
            return `<tr>
                <td class="font-medium">${s.service_name}</td>
                <td>${s.server_hostname || 'Server #' + s.server}</td>
                <td><span class="badge badge-neutral">${s.service_type || '-'}</span></td>
                <td><span class="badge ${statusBadge}">${s.status}</span></td>
                <td style="font-size:var(--fs-sm);color:var(--clr-text-muted)">${restart}</td>
                <td style="display:flex;gap:4px;flex-wrap:wrap;">
                    ${s.status !== 'running' ? `<button class="btn btn-sm btn-outline" style="color:var(--clr-success);border-color:var(--clr-success)" onclick="ServicesPage.execAction(${s.id},'start')">Start</button>` : ''}
                    ${s.status === 'running' ? `<button class="btn btn-sm btn-outline" style="color:var(--clr-danger);border-color:var(--clr-danger)" onclick="ServicesPage.execAction(${s.id},'stop')">Stop</button>` : ''}
                    <button class="btn btn-sm btn-outline" onclick="ServicesPage.execAction(${s.id},'restart')">Restart</button>
                    <button class="btn btn-sm btn-outline" onclick="ServicesPage.editService(${s.id})">Edit</button>
                    <button class="btn btn-sm btn-outline" style="color:var(--clr-danger);border-color:var(--clr-danger)" onclick="ServicesPage.deleteService(${s.id},'${s.service_name}')">Del</button>
                </td>
            </tr>`;
        }).join('');
    }

    function filterData() {
        const q = (document.getElementById('svc-search')?.value || '').toLowerCase();
        if (!q) return renderTable(allServices);
        renderTable(allServices.filter(s => s.service_name.toLowerCase().includes(q) || (s.server_hostname || '').toLowerCase().includes(q) || (s.service_type || '').toLowerCase().includes(q)));
    }

    function _serverOptions(selectedId) {
        return serversList.map(s => `<option value="${s.id}" ${s.id === selectedId ? 'selected' : ''}>${s.hostname}</option>`).join('');
    }

    function _formHtml(data = {}) {
        return `<div style="display:grid;gap:var(--space-4);">
            <div class="form-group"><label class="form-label">Service Name *</label><input class="form-input" id="svc-name" value="${data.service_name || ''}" placeholder="nginx"></div>
            <div class="form-group"><label class="form-label">Server *</label><select class="form-input" id="svc-server">${_serverOptions(data.server)}</select></div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4);">
                <div class="form-group"><label class="form-label">Type</label><input class="form-input" id="svc-type" value="${data.service_type || ''}" placeholder="Web Server"></div>
                <div class="form-group"><label class="form-label">Status</label><select class="form-input" id="svc-status">
                    <option value="running" ${data.status === 'running' ? 'selected' : ''}>Running</option>
                    <option value="stopped" ${data.status === 'stopped' ? 'selected' : ''}>Stopped</option>
                </select></div>
            </div>
        </div>`;
    }

    function _getFormData() {
        return { service_name: document.getElementById('svc-name').value.trim(), server: parseInt(document.getElementById('svc-server').value), service_type: document.getElementById('svc-type').value.trim(), status: document.getElementById('svc-status').value };
    }

    function openAddModal() { Modal.open(window.t('Add Service'), _formHtml(), `<button class="btn btn-primary" onclick="ServicesPage.submitAdd()">Create</button>`); }

    async function submitAdd() {
        const data = _getFormData();
        if (!data.service_name) return Toast.error('Service name is required.');
        try { await API.post('/api/system-admin/services/', data); Toast.success('Service created!'); Modal.close(); loadData(); } catch (e) { Toast.error('Failed: ' + e.message); }
    }

    async function editService(id) {
        const svc = allServices.find(s => s.id === id);
        if (!svc) return;
        Modal.open(window.t('Edit Service'), _formHtml(svc), `<button class="btn btn-primary" onclick="ServicesPage.submitEdit(${id})">Save</button>`);
    }

    async function submitEdit(id) {
        const data = _getFormData();
        try { await API.patch('/api/system-admin/services/' + id + '/', data); Toast.success('Service updated!'); Modal.close(); loadData(); } catch (e) { Toast.error('Failed: ' + e.message); }
    }

    async function execAction(id, action) {
        try {
            const res = await API.post('/api/system-admin/services/' + id + '/execute_command/', { action });
            Toast.success(`Action '${action}' executed. ${res.output || res.message || ''}`);
            loadData();
        } catch (e) { Toast.error('Action failed: ' + e.message); }
    }

    async function deleteService(id, name) {
        Modal.open(window.t('Delete Service'), `<div style="text-align:center;padding:16px;"><h3>Delete "${name}"?</h3><p style="color:var(--clr-text-muted)">This action cannot be undone.</p></div>`,
            `<button class="btn btn-outline" onclick="Modal.close()">Cancel</button><button class="btn" style="background:var(--clr-danger);color:white" onclick="ServicesPage.confirmDelete(${id})">Delete</button>`);
    }
    async function confirmDelete(id) { try { await API.delete('/api/system-admin/services/' + id + '/'); Toast.success('Service deleted.'); Modal.close(); loadData(); } catch (e) { Toast.error('Failed: ' + e.message); } }

    return { render, loadData, filterData, openAddModal, submitAdd, editService, submitEdit, execAction, deleteService, confirmDelete };
})();
window.ServicesPage = ServicesPage;

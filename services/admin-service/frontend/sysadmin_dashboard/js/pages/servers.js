const ServersPage = (() => {
    let allServers = [];

    function render(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h2>${window.t('Servers Inventory')}</h2>
                    <p class="text-secondary">${window.t('Manage system infrastructure, operating systems, and services.')}</p>
                </div>
                <div class="header-actions">
                    <button class="btn btn-primary" onclick="ServersPage.openAddServerModal()">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                            <line x1="12" y1="5" x2="12" y2="19"></line>
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                        ${window.t('Add Server')}
                    </button>
                </div>
            </div>

            <div class="card">
                <div class="table-actions">
                    <div class="form-search" style="width: 320px; max-width: 100%;">
                        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                            <circle cx="11" cy="11" r="8"></circle>
                            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                        </svg>
                        <input type="text" class="form-input" id="server-search" placeholder="${window.t('Search servers...')}" oninput="ServersPage.filterData()">
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table" id="servers-table">
                        <thead>
                            <tr>
                                <th>${window.t('Hostname')}</th>
                                <th>${window.t('IP Address')}</th>
                                <th>${window.t('OS Type')}</th>
                                <th>${window.t('Environment')}</th>
                                <th>${window.t('Status')}</th>
                                <th>${window.t('Actions')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="6" class="text-center py-4"><div style="display:flex;flex-direction:column;align-items:center;padding:32px 0;"><div class="spinner" style="margin-bottom:16px;"></div><p style="color:var(--clr-text-muted)">Loading servers...</p></div></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        loadData();
    }

    async function loadData() {
        try {
            const data = await API.get('/api/system-admin/servers/');
            allServers = Array.isArray(data) ? data : (data.results || []);
            renderTable(allServers);
        } catch (error) {
            document.querySelector('#servers-table tbody').innerHTML = `<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--clr-danger)">Failed to load servers: ${error.message}</td></tr>`;
        }
    }

    function renderTable(data) {
        const tbody = document.querySelector('#servers-table tbody');
        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--clr-text-muted)"><h3>No servers found.</h3></td></tr>`;
            return;
        }
        tbody.innerHTML = data.map(s => `
            <tr>
                <td class="font-medium">${s.hostname}</td>
                <td style="font-family:var(--font-mono);font-size:var(--fs-sm)">${s.ip_address}</td>
                <td>${s.os_type} ${s.os_version}</td>
                <td><span class="badge badge-info">${s.environment}</span></td>
                <td><span class="badge badge-${s.status === 'active' ? 'success' : s.status === 'maintenance' ? 'warning' : 'danger'}">${s.status}</span></td>
                <td style="display:flex;gap:4px;">
                    <button class="btn btn-sm btn-outline" onclick="ServersPage.editServer(${s.id})">${window.t('Edit')}</button>
                    <button class="btn btn-sm btn-outline" style="color:var(--clr-danger);border-color:var(--clr-danger)" onclick="ServersPage.deleteServer(${s.id},'${s.hostname}')">${window.t('Delete')}</button>
                </td>
            </tr>
        `).join('');
    }

    function filterData() {
        const q = (document.getElementById('server-search')?.value || '').toLowerCase();
        if (!q) return renderTable(allServers);
        renderTable(allServers.filter(s => s.hostname.toLowerCase().includes(q) || s.ip_address.includes(q) || s.environment.toLowerCase().includes(q)));
    }

    function _serverFormHtml(data = {}) {
        return `
            <div style="display:grid;gap:var(--space-4);">
                <div class="form-group"><label class="form-label">Hostname *</label>
                    <input type="text" class="form-input" id="srv-hostname" value="${data.hostname || ''}" placeholder="web-prod-01.craft.local" required></div>
                <div class="form-group"><label class="form-label">IP Address *</label>
                    <input type="text" class="form-input" id="srv-ip" value="${data.ip_address || ''}" placeholder="10.0.1.10" required></div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4);">
                    <div class="form-group"><label class="form-label">OS Type *</label>
                        <input type="text" class="form-input" id="srv-os-type" value="${data.os_type || ''}" placeholder="Ubuntu"></div>
                    <div class="form-group"><label class="form-label">OS Version *</label>
                        <input type="text" class="form-input" id="srv-os-version" value="${data.os_version || ''}" placeholder="22.04 LTS"></div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4);">
                    <div class="form-group"><label class="form-label">Environment *</label>
                        <select class="form-input" id="srv-env">
                            <option value="production" ${data.environment === 'production' ? 'selected' : ''}>Production</option>
                            <option value="staging" ${data.environment === 'staging' ? 'selected' : ''}>Staging</option>
                            <option value="development" ${data.environment === 'development' ? 'selected' : ''}>Development</option>
                        </select></div>
                    <div class="form-group"><label class="form-label">Status *</label>
                        <select class="form-input" id="srv-status">
                            <option value="active" ${data.status === 'active' ? 'selected' : ''}>Active</option>
                            <option value="inactive" ${data.status === 'inactive' ? 'selected' : ''}>Inactive</option>
                            <option value="maintenance" ${data.status === 'maintenance' ? 'selected' : ''}>Maintenance</option>
                        </select></div>
                </div>
            </div>`;
    }

    function _getFormData() {
        return {
            hostname: document.getElementById('srv-hostname').value.trim(),
            ip_address: document.getElementById('srv-ip').value.trim(),
            os_type: document.getElementById('srv-os-type').value.trim(),
            os_version: document.getElementById('srv-os-version').value.trim(),
            environment: document.getElementById('srv-env').value,
            status: document.getElementById('srv-status').value
        };
    }

    function openAddServerModal() {
        Modal.open(window.t('Add Server'), _serverFormHtml(), `
            <button class="btn btn-primary" onclick="ServersPage.submitAdd()">Create Server</button>
        `);
    }

    async function submitAdd() {
        const data = _getFormData();
        if (!data.hostname || !data.ip_address) return Toast.error('Hostname and IP are required.');
        try {
            await API.post('/api/system-admin/servers/', data);
            Toast.success('Server created successfully!');
            Modal.close();
            loadData();
        } catch (e) { Toast.error('Failed to create server: ' + (e.message || 'Unknown error')); }
    }

    async function editServer(id) {
        const server = allServers.find(s => s.id === id);
        if (!server) return Toast.error('Server not found');
        Modal.open(window.t('Edit Server'), _serverFormHtml(server), `
            <button class="btn btn-primary" onclick="ServersPage.submitEdit(${id})">Save Changes</button>
        `);
    }

    async function submitEdit(id) {
        const data = _getFormData();
        if (!data.hostname || !data.ip_address) return Toast.error('Hostname and IP are required.');
        try {
            await API.patch('/api/system-admin/servers/' + id + '/', data);
            Toast.success('Server updated successfully!');
            Modal.close();
            loadData();
        } catch (e) { Toast.error('Failed to update server: ' + (e.message || 'Unknown error')); }
    }

    async function deleteServer(id, hostname) {
        Modal.open(window.t('Delete Server'), `
            <div style="text-align:center;padding:var(--space-4);">
                <svg viewBox="0 0 24 24" fill="none" stroke="var(--clr-danger)" stroke-width="2" width="48" height="48" style="margin-bottom:16px;"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                <h3 style="margin-bottom:8px;">Are you sure?</h3>
                <p style="color:var(--clr-text-muted);">This will permanently delete <strong>${hostname}</strong> and all associated services, users, cron jobs, and backups.</p>
            </div>`, `
            <button class="btn btn-outline" onclick="Modal.close()">Cancel</button>
            <button class="btn" style="background:var(--clr-danger);color:white;" onclick="ServersPage.confirmDelete(${id})">Delete</button>
        `);
    }

    async function confirmDelete(id) {
        try {
            await API.delete('/api/system-admin/servers/' + id + '/');
            Toast.success('Server deleted.');
            Modal.close();
            loadData();
        } catch (e) { Toast.error('Failed to delete: ' + (e.message || 'Unknown error')); }
    }

    return { render, loadData, filterData, openAddServerModal, submitAdd, editServer, submitEdit, deleteServer, confirmDelete };
})();

window.ServersPage = ServersPage;

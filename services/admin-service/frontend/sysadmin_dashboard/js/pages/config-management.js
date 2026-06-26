const ConfigManagementPage = (() => {
    function render(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h2>${window.t('Configuration Management')}</h2>
                    <p class="text-secondary">${window.t('Manage environment variables and config files.')}</p>
                </div>
                <div class="header-actions">
                    <button class="btn btn-primary" onclick="Toast.show('Add config functionality coming soon.', 'info')">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                            <line x1="12" y1="5" x2="12" y2="19"></line>
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                        ${window.t('Add New')}
                    </button>
                </div>
            </div>

            <div class="card" style="margin-bottom:var(--space-6);">
                <div class="table-actions">
                    <div class="form-search" style="width: 320px; max-width: 100%;">
                        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                            <circle cx="11" cy="11" r="8"></circle>
                            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                        </svg>
                        <input type="text" class="form-input" id="config-search" placeholder="${window.t('Search...')}" oninput="ConfigManagementPage.filterData()">
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="table" id="config-table">
                        <thead>
                            <tr>
                                <th>${window.t('Name')}</th>
                                <th>${window.t('Server')}</th>
                                <th>${window.t('Type')}</th>
                                <th>${window.t('Status')}</th>
                                <th>${window.t('Last Modified')}</th>
                                <th>${window.t('Actions')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="6" class="text-center py-4"><div style="display:flex;flex-direction:column;align-items:center;padding:32px 0;"><div class="spinner" style="margin-bottom:16px;"></div><p style="color:var(--clr-text-muted)">Loading configurations...</p></div></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        loadData();
    }

    let allData = [];

    async function loadData() {
        try {
            // Build config entries from services and cron jobs
            const [services, cronJobs, servers] = await Promise.all([
                API.get('/api/system-admin/services/'),
                API.get('/api/system-admin/cron-jobs/'),
                API.get('/api/system-admin/servers/')
            ]);

            const serverMap = {};
            (Array.isArray(servers) ? servers : (servers.results || [])).forEach(s => serverMap[s.id] = s.hostname);

            allData = [];

            // Add service configs
            const svcList = Array.isArray(services) ? services : (services.results || []);
            svcList.forEach(svc => {
                allData.push({
                    name: `/etc/${svc.service_name}/${svc.service_name}.conf`,
                    server: serverMap[svc.server] || `Server #${svc.server}`,
                    type: 'Service Config',
                    status: svc.status === 'running' ? 'active' : 'inactive',
                    last_modified: svc.last_restart || new Date().toISOString()
                });
            });

            // Add cron configs
            const cronList = Array.isArray(cronJobs) ? cronJobs : (cronJobs.results || []);
            cronList.forEach(cj => {
                allData.push({
                    name: cj.name,
                    server: serverMap[cj.server] || `Server #${cj.server}`,
                    type: 'Cron Schedule',
                    status: cj.status === 'active' ? 'active' : 'disabled',
                    last_modified: new Date().toISOString()
                });
            });

            // Add env files for each server
            Object.entries(serverMap).forEach(([id, hostname]) => {
                allData.push({
                    name: '/app/.env',
                    server: hostname,
                    type: 'Environment',
                    status: 'active',
                    last_modified: new Date().toISOString()
                });
            });

            renderTable(allData);
        } catch(e) {
            document.querySelector('#config-table tbody').innerHTML = `<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--clr-text-muted)">${window.t('Failed to load configurations')}: ${e.message}</td></tr>`;
        }
    }

    function renderTable(data) {
        const tbody = document.querySelector('#config-table tbody');
        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
                <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; padding:32px 0;">
                    <h3>${window.t('No Data Available')}</h3>
                    <p style="color:var(--clr-text-muted)">${window.t('No configurations found.')}</p>
                </div>
            </td></tr>`;
            return;
        }

        tbody.innerHTML = data.map(item => {
            const statusClass = item.status === 'active' ? 'badge-success' : item.status === 'disabled' ? 'badge-warning' : 'badge-neutral';
            const date = item.last_modified ? new Date(item.last_modified).toLocaleDateString() : '-';
            return `<tr>
                <td><span style="font-family:var(--font-mono);font-size:var(--fs-sm)">${item.name}</span></td>
                <td>${item.server}</td>
                <td><span class="badge badge-neutral">${item.type}</span></td>
                <td><span class="badge ${statusClass}">${item.status}</span></td>
                <td style="font-size:var(--fs-sm);color:var(--clr-text-muted)">${date}</td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="Toast.show('View config: ${item.name}', 'info')">View</button>
                </td>
            </tr>`;
        }).join('');
    }

    function filterData() {
        const q = (document.getElementById('config-search')?.value || '').toLowerCase();
        if (!q) return renderTable(allData);
        renderTable(allData.filter(d => d.name.toLowerCase().includes(q) || d.server.toLowerCase().includes(q) || d.type.toLowerCase().includes(q)));
    }

    return { render, loadData, filterData };
})();

window.ConfigManagementPage = ConfigManagementPage;

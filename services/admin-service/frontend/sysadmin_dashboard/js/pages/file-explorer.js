const FileExplorerPage = (() => {
    function render(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h2>${window.t('File Explorer')}</h2>
                    <p class="text-secondary">${window.t('Browse directories and manage file permissions.')}</p>
                </div>
                <div class="header-actions">
                    <button class="btn btn-primary" onclick="Toast.show('Upload functionality coming soon.', 'info')">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
                        </svg>
                        ${window.t('Upload File')}
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
                        <input type="text" class="form-input" id="file-search" placeholder="${window.t('Search files...')}" oninput="FileExplorerPage.filterData()">
                    </div>
                </div>

                <div id="file-breadcrumb" style="padding:var(--space-3) var(--space-4);border-bottom:1px solid var(--clr-border);font-size:var(--fs-sm);">
                    <span style="color:var(--clr-text-muted)">Path:</span>
                    <span style="font-family:var(--font-mono);color:var(--clr-primary);cursor:pointer;" onclick="FileExplorerPage.navigate('/')">/</span>
                </div>

                <div class="table-responsive">
                    <table class="table" id="file-table">
                        <thead>
                            <tr>
                                <th></th>
                                <th>${window.t('Name')}</th>
                                <th>${window.t('Server')}</th>
                                <th>${window.t('Size')}</th>
                                <th>${window.t('Permissions')}</th>
                                <th>${window.t('Actions')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="6" class="text-center py-4"><div style="display:flex;flex-direction:column;align-items:center;padding:32px 0;"><div class="spinner" style="margin-bottom:16px;"></div><p style="color:var(--clr-text-muted)">Loading file system...</p></div></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        loadData();
    }

    let allFiles = [];
    let currentPath = '/';

    async function loadData() {
        try {
            const [servers, diskVolumes, scripts] = await Promise.all([
                API.get('/api/system-admin/servers/'),
                API.get('/api/system-admin/disk-volumes/'),
                API.get('/api/system-admin/scripts/')
            ]);

            const serverList = Array.isArray(servers) ? servers : (servers.results || []);
            const diskList = Array.isArray(diskVolumes) ? diskVolumes : (diskVolumes.results || []);
            const scriptList = Array.isArray(scripts) ? scripts : (scripts.results || []);
            const serverMap = {};
            serverList.forEach(s => serverMap[s.id] = s.hostname);

            allFiles = [];

            // Root directories
            allFiles.push({ type: 'dir', name: 'app', path: '/app', server: serverList[0]?.hostname || '-', size: '-', perms: 'drwxr-xr-x' });
            allFiles.push({ type: 'dir', name: 'etc', path: '/etc', server: serverList[0]?.hostname || '-', size: '-', perms: 'drwxr-xr-x' });
            allFiles.push({ type: 'dir', name: 'var', path: '/var', server: serverList[0]?.hostname || '-', size: '-', perms: 'drwxr-xr-x' });
            allFiles.push({ type: 'dir', name: 'home', path: '/home', server: serverList[0]?.hostname || '-', size: '-', perms: 'drwxr-xr-x' });
            allFiles.push({ type: 'dir', name: 'backups', path: '/backups', server: serverList[0]?.hostname || '-', size: '-', perms: 'drwxr-x---' });

            // Config files from disk volumes
            diskList.forEach(dv => {
                allFiles.push({
                    type: 'dir',
                    name: dv.mount_point.split('/').pop() || dv.mount_point,
                    path: dv.mount_point,
                    server: serverMap[dv.server] || `Server #${dv.server}`,
                    size: `${dv.used} / ${dv.size}`,
                    perms: 'drwxr-xr-x'
                });
            });

            // Important config files
            const configFiles = [
                { name: 'nginx.conf', path: '/etc/nginx/nginx.conf', size: '2.4 KB', perms: '-rw-r--r--' },
                { name: 'postgresql.conf', path: '/etc/postgresql/16/main/postgresql.conf', size: '28 KB', perms: '-rw-r-----' },
                { name: 'pg_hba.conf', path: '/etc/postgresql/16/main/pg_hba.conf', size: '4.7 KB', perms: '-rw-r-----' },
                { name: 'redis.conf', path: '/etc/redis/redis.conf', size: '92 KB', perms: '-rw-r-----' },
                { name: '.env', path: '/app/.env', size: '1.2 KB', perms: '-rw-------' },
                { name: 'settings.py', path: '/app/Handcrafts/settings.py', size: '8.5 KB', perms: '-rw-r--r--' },
                { name: 'docker-compose.yml', path: '/app/docker-compose.yml', size: '3.1 KB', perms: '-rw-r--r--' },
                { name: 'Dockerfile', path: '/app/Dockerfile', size: '1.8 KB', perms: '-rw-r--r--' },
                { name: 'requirements.txt', path: '/app/requirements.txt', size: '890 B', perms: '-rw-r--r--' },
                { name: 'gunicorn.conf.py', path: '/app/gunicorn.conf.py', size: '1.1 KB', perms: '-rw-r--r--' },
            ];
            configFiles.forEach(cf => {
                allFiles.push({ type: 'file', ...cf, server: serverList[0]?.hostname || '-' });
            });

            // Scripts as files
            scriptList.forEach(sc => {
                allFiles.push({
                    type: 'file',
                    name: sc.name,
                    path: `/opt/scripts/${sc.name}`,
                    server: serverList[0]?.hostname || '-',
                    size: `${(sc.script_content || '').length} B`,
                    perms: '-rwxr-xr-x'
                });
            });

            renderTable(allFiles);
        } catch(e) {
            document.querySelector('#file-table tbody').innerHTML = `<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--clr-text-muted)">${window.t('Failed to load files')}: ${e.message}</td></tr>`;
        }
    }

    function renderTable(data) {
        const tbody = document.querySelector('#file-table tbody');
        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
                <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; padding:32px 0;">
                    <h3>${window.t('No Data Available')}</h3>
                    <p style="color:var(--clr-text-muted)">${window.t('No files found.')}</p>
                </div>
            </td></tr>`;
            return;
        }

        // Sort: directories first, then files
        const sorted = [...data].sort((a, b) => {
            if (a.type === 'dir' && b.type !== 'dir') return -1;
            if (a.type !== 'dir' && b.type === 'dir') return 1;
            return a.name.localeCompare(b.name);
        });

        tbody.innerHTML = sorted.map(item => {
            const icon = item.type === 'dir' 
                ? '<svg viewBox="0 0 24 24" fill="var(--clr-warning)" stroke="var(--clr-warning)" stroke-width="1" width="20" height="20"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>'
                : '<svg viewBox="0 0 24 24" fill="none" stroke="var(--clr-text-muted)" stroke-width="2" width="20" height="20"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>';
            
            return `<tr>
                <td style="width:32px;padding-right:0;">${icon}</td>
                <td>
                    <div style="font-weight:var(--fw-medium)">${item.name}</div>
                    <div style="font-family:var(--font-mono);font-size:var(--fs-xs);color:var(--clr-text-muted)">${item.path}</div>
                </td>
                <td style="font-size:var(--fs-sm)">${item.server}</td>
                <td style="font-size:var(--fs-sm);color:var(--clr-text-muted)">${item.size}</td>
                <td><span style="font-family:var(--font-mono);font-size:var(--fs-xs);background:var(--clr-bg-elevated);padding:2px 8px;border-radius:4px;">${item.perms}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="Toast.show('Viewing: ${item.path}', 'info')">
                        ${item.type === 'dir' ? 'Open' : 'View'}
                    </button>
                </td>
            </tr>`;
        }).join('');
    }

    function filterData() {
        const q = (document.getElementById('file-search')?.value || '').toLowerCase();
        if (!q) return renderTable(allFiles);
        renderTable(allFiles.filter(f => f.name.toLowerCase().includes(q) || f.path.toLowerCase().includes(q)));
    }

    function navigate(path) {
        currentPath = path;
        Toast.show('Navigating to: ' + path, 'info');
    }

    return { render, loadData, filterData, navigate };
})();

window.FileExplorerPage = FileExplorerPage;

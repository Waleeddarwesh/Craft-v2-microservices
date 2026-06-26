const SystemHealthPage = (() => {
    async function render(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h1 class="page-title">${window.t('System Health')}</h1>
                    <p class="page-subtitle">${window.t('Real-time monitoring of microservices and infrastructure')}</p>
                </div>
                <div class="page-actions">
                    <button class="btn btn-outline" onclick="SystemHealthPage.refreshHealth()">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
                        ${window.t('Refresh')}
                    </button>
                </div>
            </div>

            <h3 class="mt-4 mb-3">${window.t('Core Services')}</h3>
            <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px;" id="health-cards-container">
                <div class="card skeleton" style="height: 120px;"></div>
                <div class="card skeleton" style="height: 120px;"></div>
                <div class="card skeleton" style="height: 120px;"></div>
                <div class="card skeleton" style="height: 120px;"></div>
            </div>

            <h3 class="mt-4 mb-3">${window.t('Monitoring & Observability')}</h3>
            <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px;" id="monitoring-cards-container">
                <div class="card skeleton" style="height: 120px;"></div>
                <div class="card skeleton" style="height: 120px;"></div>
            </div>

            <h3 class="mt-4 mb-3">${window.t('Infrastructure Summary')}</h3>
            <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;" id="infra-stats-container">
                <div class="card skeleton" style="height: 100px;"></div>
                <div class="card skeleton" style="height: 100px;"></div>
                <div class="card skeleton" style="height: 100px;"></div>
                <div class="card skeleton" style="height: 100px;"></div>
            </div>

            <div class="card" style="margin-top: 24px;">
                <h3 style="margin-bottom: 16px; font-weight: var(--fw-semibold);">${window.t('Service Status Overview')}</h3>
                <p style="color: var(--clr-text-muted); font-size: var(--fs-sm);">${window.t('This page polls the backend services directly to ensure they are responding. Monitoring tools (Prometheus/Grafana) check external endpoints configured in the system.')}</p>
            </div>
        `;

        await fetchHealth();
    }

    async function fetchHealth() {
        const container = document.getElementById('health-cards-container');
        const monContainer = document.getElementById('monitoring-cards-container');
        const infraContainer = document.getElementById('infra-stats-container');
        if (!container) return;

        try {
            const data = await API.get('/admin-api/health/');

            // Core services
            const services = [
                { name: 'PostgreSQL DB', key: 'database', icon: '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline>' },
                { name: 'Redis Cache', key: 'redis', icon: '<rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line>' },
                { name: 'RabbitMQ Broker', key: 'rabbitmq', icon: '<polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline>' },
                { name: 'Celery Workers', key: 'celery', icon: '<circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline>' }
            ];

            container.innerHTML = services.map(s => _renderHealthCard(s.name, data[s.key] === 'up', s.icon)).join('');

            // Monitoring services
            const monServices = [
                { name: 'Prometheus', key: 'prometheus', url: data.prometheus_url || null, icon: '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>' },
                { name: 'Grafana', key: 'grafana', url: data.grafana_url || null, icon: '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/>' }
            ];

            if (monContainer) {
                monContainer.innerHTML = monServices.map(s => {
                    const isUp = data[s.key] === 'up';
                    const statusColor = isUp ? 'var(--clr-success)' : 'var(--clr-text-muted)';
                    const statusText = isUp ? window.t('Operational') : window.t('Not Configured');
                    const bgColor = isUp ? 'rgba(34, 197, 94, 0.1)' : 'rgba(148, 163, 184, 0.1)';

                    return `<div class="card" style="display:flex; align-items:center; gap: 16px; padding: 24px;">
                        <div style="width:48px;height:48px;border-radius:12px;background:${bgColor};color:${statusColor};display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${s.icon}</svg>
                        </div>
                        <div style="flex:1;">
                            <div style="font-weight:var(--fw-semibold);font-size:var(--fs-md);color:var(--clr-text);margin-bottom:4px;">${window.t(s.name)}</div>
                            <div style="display:flex;align-items:center;gap:6px;font-size:var(--fs-sm);color:${statusColor};font-weight:var(--fw-medium);">
                                <span style="width:8px;height:8px;border-radius:50%;background:${statusColor};display:inline-block;"></span>
                                ${statusText}
                            </div>
                        </div>
                        ${s.url ? `<a href="${s.url}" target="_blank" class="btn btn-sm btn-outline">Open</a>` : ''}
                    </div>`;
                }).join('');
            }

            // Infrastructure stats
            if (infraContainer) {
                try {
                    const [servers, services, containers, incidents] = await Promise.all([
                        API.get('/api/system-admin/servers/'),
                        API.get('/api/system-admin/services/'),
                        API.get('/api/system-admin/containers/'),
                        API.get('/api/system-admin/incidents/')
                    ]);
                    const srvList = Array.isArray(servers) ? servers : (servers.results || []);
                    const svcList = Array.isArray(services) ? services : (services.results || []);
                    const ctList = Array.isArray(containers) ? containers : (containers.results || []);
                    const incList = Array.isArray(incidents) ? incidents : (incidents.results || []);
                    const activeServers = srvList.filter(s => s.status === 'active').length;
                    const runningSvcs = svcList.filter(s => s.status === 'running').length;
                    const runningCts = ctList.filter(c => c.state === 'running').length;
                    const openIncidents = incList.filter(i => i.status === 'open' || i.status === 'investigating').length;

                    infraContainer.innerHTML = `
                        ${_renderStatCard('Servers', `${activeServers}/${srvList.length}`, 'active', 'var(--clr-success)')}
                        ${_renderStatCard('Services', `${runningSvcs}/${svcList.length}`, 'running', 'var(--clr-info)')}
                        ${_renderStatCard('Containers', `${runningCts}/${ctList.length}`, 'running', 'var(--clr-primary)')}
                        ${_renderStatCard('Open Incidents', `${openIncidents}`, openIncidents > 0 ? 'attention needed' : 'all clear', openIncidents > 0 ? 'var(--clr-warning)' : 'var(--clr-success)')}
                    `;
                } catch(e) {
                    infraContainer.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:24px;color:var(--clr-text-muted)">Could not load infrastructure stats.</div>`;
                }
            }

        } catch (e) {
            container.innerHTML = `<div class="empty-state" style="grid-column: 1 / -1; color: var(--clr-danger); padding: 40px; text-align: center;">${window.t('Failed to load system health data.')}</div>`;
            if (monContainer) monContainer.innerHTML = '';
            if (infraContainer) infraContainer.innerHTML = '';
        }
    }

    function _renderHealthCard(name, isUp, icon) {
        const statusColor = isUp ? 'var(--clr-success)' : 'var(--clr-danger)';
        const statusText = isUp ? window.t('Operational') : window.t('Down');
        const bgColor = isUp ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)';
        return `<div class="card" style="display:flex; align-items:center; gap: 16px; padding: 24px;">
            <div style="width:48px;height:48px;border-radius:12px;background:${bgColor};color:${statusColor};display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${icon}</svg>
            </div>
            <div>
                <div style="font-weight:var(--fw-semibold);font-size:var(--fs-md);color:var(--clr-text);margin-bottom:4px;">${window.t(name)}</div>
                <div style="display:flex;align-items:center;gap:6px;font-size:var(--fs-sm);color:${statusColor};font-weight:var(--fw-medium);">
                    <span style="width:8px;height:8px;border-radius:50%;background:${statusColor};display:inline-block;"></span>
                    ${statusText}
                </div>
            </div>
        </div>`;
    }

    function _renderStatCard(label, value, subtitle, color) {
        return `<div class="card" style="padding:20px;">
            <div style="font-size:var(--fs-xs);color:var(--clr-text-muted);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px;">${window.t(label)}</div>
            <div style="font-size:28px;font-weight:var(--fw-bold);color:${color};margin-bottom:4px;">${value}</div>
            <div style="font-size:var(--fs-xs);color:var(--clr-text-muted)">${subtitle}</div>
        </div>`;
    }

    async function refreshHealth() {
        const container = document.getElementById('health-cards-container');
        if (container) {
            container.style.opacity = '0.5';
            document.getElementById('monitoring-cards-container').style.opacity = '0.5';
            document.getElementById('infra-stats-container').style.opacity = '0.5';
            await fetchHealth();
            container.style.opacity = '1';
            document.getElementById('monitoring-cards-container').style.opacity = '1';
            document.getElementById('infra-stats-container').style.opacity = '1';
        }
    }

    return { render, refreshHealth };
})();

window.SystemHealthPage = SystemHealthPage;

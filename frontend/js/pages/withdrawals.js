/* Withdrawal Requests Page */
const WithdrawalsPage = (() => {
    const STATUS_MAP = { Requested:'warning', 'Awaiting Approval':'warning', Approved:'info', Processing:'info', Completed:'success', Rejected:'danger', Failed:'danger' };
    let allWithdrawals = [];

    async function render(container) {
        container.innerHTML = `
            <div class="page-header" style="display:flex; justify-content:space-between; align-items:center;">
                <div><h1>Withdrawal Requests</h1><p>Manage balance withdrawal requests from suppliers</p></div>
                <div class="page-header-actions" style="display:flex; gap:8px;">
                    <button class="btn btn-success" onclick="WithdrawalsPage.approveAll()">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:6px;"><path d="M20 6L9 17l-5-5"/></svg>
                        ${window.t('Approve All')}
                    </button>
                    <button class="btn btn-outline" onclick="WithdrawalsPage.exportData()">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:6px;"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                        ${window.t('Export CSV')}
                    </button>
                </div>
            </div>
            <div class="filter-bar mb-6">
                <select id="withdraw-status-filter" onchange="WithdrawalsPage.applyFilter()">
                    <option value="">All Statuses</option>
                    <option value="Requested">Requested</option>
                    <option value="Approved">Approved</option>
                    <option value="Processing">Processing</option>
                    <option value="Completed">Completed</option>
                    <option value="Rejected">Rejected</option>
                </select>
            </div>
            <div id="withdrawals-table">
                <div class="skeleton" style="height:400px; border-radius:var(--radius-lg)"></div>
            </div>`;
        await loadWithdrawals();
    }

    async function loadWithdrawals() {
        try {
            const data = await API.get('/admin-api/withdrawals/');
            allWithdrawals = data || [];
            renderTable(allWithdrawals);
        } catch(e) { document.getElementById('withdrawals-table').innerHTML = `<div class="empty-state"><h3>Could not load withdrawals</h3><p>${e.message}</p></div>`; }
    }

    function renderTable(items) {
        DataTable.render('withdrawals-table', {
            columns: [
                { key: 'id', label: 'ID', render: v => `<span style="font-family:var(--font-mono);font-size:var(--fs-xs)">${(v||'').toString().slice(0,8)}</span>` },
                { key: 'user_name', label: 'User', render: (v, r) => v || r.user || '—' },
                { key: 'user_balance', label: 'Balance', render: v => `<span style="color:var(--clr-primary);font-weight:var(--fw-medium)">EGP ${parseFloat(v||0).toFixed(2)}</span>` },
                { key: 'amount', label: 'Amount', render: v => `EGP ${parseFloat(v||0).toFixed(2)}` },
                { key: 'transfer_type', label: 'Method' },
                { key: 'transfer_number', label: 'Transfer #' },
                { key: 'risk_score', label: 'Risk', render: v => {
                    const n = parseFloat(v||0); const cls = n > 70 ? 'danger' : n > 30 ? 'warning' : 'success';
                    return `<span class="badge badge-${cls}">${n.toFixed(0)}%</span>`;
                }},
                { key: 'transfer_status', label: 'Status', render: v => `<span class="badge badge-${STATUS_MAP[v]||'neutral'} badge-dot">${v||''}</span>` },
                { key: '_actions', label: 'Actions', render: (_, row) => {
                    if (row.transfer_status === 'Requested' || row.transfer_status === 'Awaiting Approval') {
                        return `<div style="display:flex;gap:var(--space-2)">
                            <button class="btn btn-sm btn-success" onclick="WithdrawalsPage.action('${row.id}','approve')">Approve</button>
                            <button class="btn btn-sm btn-danger" onclick="WithdrawalsPage.action('${row.id}','reject')">Reject</button>
                        </div>`;
                    }
                    return `<button class="btn btn-sm btn-ghost" onclick="WithdrawalsPage.view('${row.id}')">View</button>`;
                }}
            ],
            data: items
        });
    }

    function applyFilter() {
        const status = document.getElementById('withdraw-status-filter').value;
        renderTable(status ? allWithdrawals.filter(w => w.transfer_status === status) : allWithdrawals);
    }

    async function action(id, act) {
        const w = allWithdrawals.find(x => x.id === id);
        if (!w) return;
        
        let balText = `<div style="margin-top:16px;padding:12px;background:var(--clr-surface-alt);border-radius:var(--radius-md);border:1px solid var(--clr-surface-border)">
            <div style="display:flex;justify-content:space-between;margin-bottom:8px"><span>${window.t('Requested Amount')}:</span><strong style="color:var(--clr-danger)">EGP ${parseFloat(w.amount||0).toFixed(2)}</strong></div>
            <div style="display:flex;justify-content:space-between"><span>${window.t('User Balance')}:</span><strong style="color:var(--clr-primary)">EGP ${parseFloat(w.user_balance||0).toFixed(2)}</strong></div>
        </div>`;

        if (act === 'reject') {
            balText += `
            <div style="margin-top:16px;">
                <label style="display:block;margin-bottom:8px;font-size:var(--fs-xs);font-weight:var(--fw-medium);color:var(--clr-text)">${window.t('Rejection Reason')}</label>
                <select id="withdraw-reject-reason" style="width:100%;padding:8px;border-radius:var(--radius-md);border:1px solid var(--clr-surface-border);background:var(--clr-surface);margin-bottom:12px;color:var(--clr-text)">
                    <option value="Suspicious Activity">${window.t('Suspicious Activity')}</option>
                    <option value="Invalid Bank Details">${window.t('Invalid Bank Details')}</option>
                    <option value="Account Under Review">${window.t('Account Under Review')}</option>
                    <option value="Other">${window.t('Other (Please specify below)')}</option>
                </select>
                <label style="display:block;margin-bottom:8px;font-size:var(--fs-xs);font-weight:var(--fw-medium);color:var(--clr-text)">${window.t('Additional Notes (Optional)')}</label>
                <textarea id="withdraw-admin-notes" style="width:100%;padding:8px;border-radius:var(--radius-md);border:1px solid var(--clr-surface-border);background:var(--clr-surface);min-height:80px;color:var(--clr-text)" placeholder="${window.t('Enter any notes for the user...')}"></textarea>
            </div>`;
        }

        Modal.confirm(window.t(`${act.charAt(0).toUpperCase()+act.slice(1)} Withdrawal`), window.t(`Are you sure you want to ${act} this withdrawal request?`) + balText, async () => {
            try {
                let adminNotes = '';
                if (act === 'reject') {
                    const reason = document.getElementById('withdraw-reject-reason')?.value || '';
                    const notes = document.getElementById('withdraw-admin-notes')?.value || '';
                    adminNotes = reason + (notes ? ': ' + notes : '');
                } else {
                    adminNotes = 'Approved manually.';
                }
                
                await API.post(`/admin-api/withdrawals/${id}/action/`, { action: act, admin_notes: adminNotes });
                Toast.success(window.t(`Withdrawal ${act}d successfully`));
                
                if (w) {
                    w.transfer_status = act === 'approve' ? 'Approved' : 'Rejected';
                    w.admin_notes = adminNotes;
                }
                
                const status = document.getElementById('withdraw-status-filter').value;
                if (status && w.transfer_status !== status) {
                    applyFilter();
                } else {
                    const dt = DataTable._instances['withdrawals-table'];
                    if (dt) dt.update();
                }
            } catch(e) { Toast.error(e.message); }
        }, window.t(act.charAt(0).toUpperCase()+act.slice(1)), act === 'approve' ? 'success' : 'danger');
    }

    async function approveAll() {
        const pending = allWithdrawals.filter(w => w.transfer_status === 'Requested' || w.transfer_status === 'Awaiting Approval');
        if (pending.length === 0) {
            Toast.info(window.t('No pending withdrawals to approve'));
            return;
        }

        const balText = `<div style="margin-top:16px;padding:12px;background:var(--clr-surface-alt);border-radius:var(--radius-md);border:1px solid var(--clr-surface-border)">
            <div style="display:flex;justify-content:space-between;margin-bottom:8px"><span>${window.t('Total Requests')}:</span><strong>${pending.length}</strong></div>
            <div style="display:flex;justify-content:space-between"><span>${window.t('Total Amount')}:</span><strong style="color:var(--clr-danger)">EGP ${pending.reduce((sum, w) => sum + parseFloat(w.amount||0), 0).toFixed(2)}</strong></div>
        </div>`;

        Modal.confirm(window.t('Approve All'), window.t('Are you sure you want to approve all pending withdrawal requests?') + balText, async () => {
            try {
                let successCount = 0;
                Toast.show(window.t('Processing approvals...'), 'info');
                
                // Process sequentially to not overload backend
                for (const w of pending) {
                    try {
                        await API.post(`/admin-api/withdrawals/${w.id}/action/`, { action: 'approve' });
                        successCount++;
                    } catch (err) {
                        console.error('Failed to approve', w.id, err);
                    }
                }
                
                Toast.success(window.t(`Successfully approved ${successCount} requests`));
                await loadWithdrawals();
            } catch(e) { Toast.error(e.message); }
        }, window.t('Approve All'), 'success');
    }

    async function view(id) {
        const w = allWithdrawals.find(x => x.id === id);
        if (!w) return;
        Modal.open(window.t('Withdrawal Details'), `<div class="detail-grid">
            <div class="detail-item"><span class="detail-label">${window.t('User')}</span><span class="detail-value">${window.t(w.user_name || '')}</span></div>
            <div class="detail-item"><span class="detail-label">${window.t('User Balance')}</span><span class="detail-value" style="color:var(--clr-primary)">EGP ${parseFloat(w.user_balance||0).toFixed(2)}</span></div>
            <div class="detail-item"><span class="detail-label">${window.t('Amount')}</span><span class="detail-value">EGP ${parseFloat(w.amount||0).toFixed(2)}</span></div>
            <div class="detail-item"><span class="detail-label">${window.t('Status')}</span><span class="detail-value"><span class="badge badge-${STATUS_MAP[w.transfer_status]||'neutral'}">${window.t(w.transfer_status)}</span></span></div>
            <div class="detail-item"><span class="detail-label">Method</span><span class="detail-value">${w.transfer_type||''}</span></div>
            <div class="detail-item"><span class="detail-label">Transfer #</span><span class="detail-value">${w.transfer_number||''}</span></div>
            <div class="detail-item"><span class="detail-label">Risk Score</span><span class="detail-value">${parseFloat(w.risk_score||0).toFixed(1)}%</span></div>
            <div class="detail-item"><span class="detail-label">Date</span><span class="detail-value">${w.created_at ? new Date(w.created_at).toLocaleString() : ''}</span></div>
        </div>${w.notes ? `<div class="mt-4"><strong style="font-size:var(--fs-sm)">Notes:</strong><p style="font-size:var(--fs-sm);color:var(--clr-text-secondary);margin-top:var(--space-1)">${w.notes}</p></div>` : ''}
        ${w.admin_notes ? `<div class="mt-4"><strong style="font-size:var(--fs-sm)">Admin Notes:</strong><p style="font-size:var(--fs-sm);color:var(--clr-text-secondary);margin-top:var(--space-1)">${w.admin_notes}</p></div>` : ''}`);
    }

    function exportData() {
        const headers = ['ID', 'User', 'Amount', 'Method', 'Transfer #', 'Risk Score %', 'Status', 'Date'];
        const dataRows = allWithdrawals.map(w => [
            w.id || '',
            w.user_name || w.user || '',
            parseFloat(w.amount || 0).toFixed(2),
            w.transfer_type || '',
            w.transfer_number || '',
            parseFloat(w.risk_score || 0).toFixed(1),
            w.transfer_status || '',
            w.created_at ? new Date(w.created_at).toLocaleDateString() : ''
        ]);
        DataExport.exportToCSV('withdrawals_export.csv', headers, dataRows);
    }

    return { render, action, view, applyFilter, exportData, approveAll };
})();

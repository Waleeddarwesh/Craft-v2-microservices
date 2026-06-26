const TeamManagementPage = (() => {
    let users = [];
    const TEAM_ROLES = [
        { value: 'SYSADMIN', label: 'System Admin' },
        { value: 'SUPPORT', label: 'Support Team' },
        { value: 'OPERATIONS', label: 'Operations Team' },
        { value: 'DEVELOPER', label: 'Developer' },
        { value: 'DB_ADMIN', label: 'Database Admin' },
        { value: 'TEST', label: 'Test Team' }
    ];

    async function loadData() {
        try {
            const data = await API.get('/admin-api/team-management/');
            users = data.team_members || [];
            renderTable();
        } catch (err) {
            Toast.error('Failed to load team members');
        }
    }

    function renderTable() {
        const tbody = document.getElementById('team-members-tbody');
        if (!tbody) return;

        if (users.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding: 20px;">No team members found.</td></tr>`;
            return;
        }

        tbody.innerHTML = users.map(user => {
            const roleLabel = TEAM_ROLES.find(r => r.value === user.team_role)?.label || user.team_role;
            return `
                <tr>
                    <td>
                        <div style="font-weight: 500">${user.full_name || 'N/A'}</div>
                        <div class="text-sm text-muted">${user.email}</div>
                    </td>
                    <td>
                        <span class="badge" style="background:var(--clr-primary); color:white;">${roleLabel}</span>
                    </td>
                    <td>${user.is_active ? '<span class="status-indicator status-active"></span> Active' : '<span class="status-indicator status-error"></span> Inactive'}</td>
                    <td>${new Date(user.date_joined).toLocaleDateString()}</td>
                    <td>
                        <button class="btn btn-sm btn-outline" onclick="TeamManagementPage.editUser(${user.id})">Edit Role</button>
                        <button class="btn btn-sm btn-outline" style="color:var(--clr-danger); border-color:var(--clr-danger)" onclick="TeamManagementPage.revokeRole(${user.id})">Revoke</button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    function getRoleOptionsHtml(selected = '') {
        return TEAM_ROLES.map(r => `<option value="${r.value}" ${r.value === selected ? 'selected' : ''}>${r.label}</option>`).join('');
    }

    function openAddModal() {
        const html = `
            <form id="team-user-form" onsubmit="event.preventDefault(); TeamManagementPage.submitUser();">
                <div class="form-group">
                    <label>Email Address</label>
                    <input type="email" id="tu-email" class="form-input" required placeholder="user@craft.com">
                </div>
                <div style="display:flex; gap:16px;">
                    <div class="form-group" style="flex:1">
                        <label>First Name</label>
                        <input type="text" id="tu-first" class="form-input" required>
                    </div>
                    <div class="form-group" style="flex:1">
                        <label>Last Name</label>
                        <input type="text" id="tu-last" class="form-input" required>
                    </div>
                </div>
                <div class="form-group">
                    <label>Team Role</label>
                    <select id="tu-role" class="form-input" required>
                        <option value="">Select a Role...</option>
                        ${getRoleOptionsHtml()}
                    </select>
                </div>
                <div class="form-group">
                    <label>Password (Required for new users)</label>
                    <input type="password" id="tu-password" class="form-input" placeholder="Leave blank to keep existing">
                </div>
                <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:24px;">
                    <button type="button" class="btn btn-outline" onclick="Modal.close()">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save User</button>
                </div>
            </form>
        `;
        Modal.open('Add / Edit Team Member', html);
    }

    window.TeamManagementPage_editUser = function(id) {
        const user = users.find(u => u.id === id);
        if (!user) return;
        
        const html = `
            <form id="team-user-form" onsubmit="event.preventDefault(); TeamManagementPage.submitUser();">
                <div class="form-group">
                    <label>Email Address</label>
                    <input type="email" id="tu-email" class="form-input" value="${user.email}" readonly style="background:#f5f5f5; cursor:not-allowed;">
                </div>
                <div style="display:flex; gap:16px;">
                    <div class="form-group" style="flex:1">
                        <label>First Name</label>
                        <input type="text" id="tu-first" class="form-input" value="${user.first_name}" required>
                    </div>
                    <div class="form-group" style="flex:1">
                        <label>Last Name</label>
                        <input type="text" id="tu-last" class="form-input" value="${user.last_name}" required>
                    </div>
                </div>
                <div class="form-group">
                    <label>Team Role</label>
                    <select id="tu-role" class="form-input" required>
                        ${getRoleOptionsHtml(user.team_role)}
                    </select>
                </div>
                <div class="form-group">
                    <label>New Password (Optional)</label>
                    <input type="password" id="tu-password" class="form-input" placeholder="Leave blank to keep existing">
                </div>
                <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:24px;">
                    <button type="button" class="btn btn-outline" onclick="Modal.close()">Cancel</button>
                    <button type="submit" class="btn btn-primary">Update User</button>
                </div>
            </form>
        `;
        Modal.open('Edit Team Member', html);
    };

    window.TeamManagementPage_revokeRole = async function(id) {
        if (!confirm('Are you sure you want to revoke this user\'s team access? They will no longer be able to log into any portal.')) return;
        
        try {
            const res = await fetch(`${Auth.getApiBase()}/admin-api/team-management/${id}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${Auth.getAccessToken()}`
                },
                body: JSON.stringify({ team_role: null })
            });
            if (res.ok) {
                Toast.success('Role revoked successfully');
                loadData();
            } else {
                Toast.error('Failed to revoke role');
            }
        } catch (err) {
            Toast.error('Network error');
        }
    };

    window.TeamManagementPage_submitUser = async function() {
        const payload = {
            email: document.getElementById('tu-email').value,
            first_name: document.getElementById('tu-first').value,
            last_name: document.getElementById('tu-last').value,
            team_role: document.getElementById('tu-role').value,
            password: document.getElementById('tu-password').value
        };

        try {
            const res = await fetch(`${Auth.getApiBase()}/admin-api/team-management/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${Auth.getAccessToken()}`
                },
                body: JSON.stringify(payload)
            });
            
            if (res.ok) {
                Toast.success('Team member saved successfully');
                Modal.close();
                loadData();
            } else {
                const data = await res.json();
                Toast.error(data.detail || 'Failed to save team member');
            }
        } catch (err) {
            Toast.error('Network error');
        }
    };

    function render(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h1 class="page-title">Team Management</h1>
                    <p class="text-muted">Manage system administrators, developers, and support teams.</p>
                </div>
                <div class="header-actions">
                    <button class="btn btn-primary" onclick="TeamManagementPage.openAddModal()">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;margin-right:8px;"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                        Add Team Member
                    </button>
                </div>
            </div>

            <div class="card">
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>User</th>
                                <th>Role</th>
                                <th>Status</th>
                                <th>Joined</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="team-members-tbody">
                            <tr><td colspan="5" style="text-align:center; padding: 20px;">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        loadData();
    }

    return { 
        render, 
        openAddModal, 
        editUser: window.TeamManagementPage_editUser, 
        revokeRole: window.TeamManagementPage_revokeRole,
        submitUser: window.TeamManagementPage_submitUser
    };
})();

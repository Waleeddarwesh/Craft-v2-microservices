const StoragePage = (() => {
    let serversList = [];
    function render(container) {
        container.innerHTML = `
            <div class="page-header"><div><h2>${window.t('Storage Administration')}</h2><p class="text-secondary">${window.t('Manage disks, mounts, and LVM volumes.')}</p></div>
                <div class="header-actions"><button class="btn btn-primary" onclick="StoragePage.openAddDiskModal()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> ${window.t('New Volume')}</button></div></div>
            <h3 class="mt-4 mb-3">${window.t('Disk Volumes')}</h3>
            <div class="card mb-4"><div class="table-responsive"><table class="table" id="disk-table"><thead><tr><th>${window.t('Mount Point')}</th><th>${window.t('Server')}</th><th>${window.t('Size')}</th><th>${window.t('Used')}</th><th>${window.t('Available')}</th><th>${window.t('Health')}</th><th>${window.t('Actions')}</th></tr></thead>
                <tbody><tr><td colspan="7" class="text-center py-4"><div class="spinner"></div></td></tr></tbody></table></div></div>
            <h3 class="mb-3">${window.t('Logical Volumes (LVM)')}</h3>
            <div class="card"><div class="table-responsive"><table class="table" id="lvm-table"><thead><tr><th>${window.t('VG Name')}</th><th>${window.t('LV Name')}</th><th>${window.t('Server')}</th><th>${window.t('Size')}</th><th>${window.t('Status')}</th><th>${window.t('Actions')}</th></tr></thead>
                <tbody><tr><td colspan="6" class="text-center py-4"><div class="spinner"></div></td></tr></tbody></table></div></div>`;
        loadData();
    }

    async function loadData() {
        try {
            const [disks, lvms, servers] = await Promise.all([
                API.get('/api/system-admin/disk-volumes/'),
                API.get('/api/system-admin/logical-volumes/'),
                API.get('/api/system-admin/servers/')
            ]);
            serversList = Array.isArray(servers) ? servers : (servers.results || []);
            const diskList = Array.isArray(disks) ? disks : (disks.results || []);
            const lvmList = Array.isArray(lvms) ? lvms : (lvms.results || []);
            // Disk Volumes
            const diskTbody = document.querySelector('#disk-table tbody');
            if (!diskList.length) { diskTbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:32px;color:var(--clr-text-muted)">No disk volumes found.</td></tr>`; }
            else { diskTbody.innerHTML = diskList.map(d => `<tr>
                <td class="font-medium"><code>${d.mount_point}</code></td>
                <td>${d.server_hostname || 'Server #'+d.server}</td><td>${d.size}</td><td>${d.used}</td><td>${d.available}</td>
                <td><span class="badge badge-${d.health==='healthy'?'success':d.health==='warning'?'warning':'danger'}">${d.health}</span></td>
                <td style="display:flex;gap:4px;"><button class="btn btn-sm btn-outline" onclick="StoragePage.editDisk(${d.id})">Edit</button><button class="btn btn-sm btn-outline" style="color:var(--clr-danger);border-color:var(--clr-danger)" onclick="StoragePage.deleteDisk(${d.id})">Del</button></td>
            </tr>`).join(''); }
            // LVM
            const lvmTbody = document.querySelector('#lvm-table tbody');
            if (!lvmList.length) { lvmTbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--clr-text-muted)">No logical volumes found.</td></tr>`; }
            else { lvmTbody.innerHTML = lvmList.map(l => `<tr>
                <td class="font-medium">${l.vg_name}</td><td class="font-medium">${l.lv_name}</td>
                <td>${l.server_hostname || 'Server #'+l.server}</td><td>${l.size}</td>
                <td><span class="badge badge-${l.status==='active'?'success':'warning'}">${l.status}</span></td>
                <td style="display:flex;gap:4px;"><button class="btn btn-sm btn-outline" onclick="StoragePage.editLvm(${l.id})">Edit</button><button class="btn btn-sm btn-outline" style="color:var(--clr-danger);border-color:var(--clr-danger)" onclick="StoragePage.deleteLvm(${l.id})">Del</button></td>
            </tr>`).join(''); }
        } catch (e) {
            document.querySelector('#disk-table tbody').innerHTML = `<tr><td colspan="7" style="text-align:center;padding:32px;color:var(--clr-danger)">Failed: ${e.message}</td></tr>`;
        }
    }

    function _srvOpts(sel) { return serversList.map(s=>`<option value="${s.id}" ${s.id===sel?'selected':''}>${s.hostname}</option>`).join(''); }

    // Disk CRUD
    function openAddDiskModal() { Modal.open(window.t('Add Disk Volume'), `<div style="display:grid;gap:var(--space-4);">
        <div class="form-group"><label class="form-label">Server *</label><select class="form-input" id="dv-server">${_srvOpts()}</select></div>
        <div class="form-group"><label class="form-label">Mount Point *</label><input class="form-input" id="dv-mount" placeholder="/var/data"></div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:var(--space-4);">
            <div class="form-group"><label class="form-label">Size</label><input class="form-input" id="dv-size" placeholder="100G"></div>
            <div class="form-group"><label class="form-label">Used</label><input class="form-input" id="dv-used" placeholder="40G"></div>
            <div class="form-group"><label class="form-label">Available</label><input class="form-input" id="dv-avail" placeholder="60G"></div>
        </div>
        <div class="form-group"><label class="form-label">Health</label><select class="form-input" id="dv-health"><option value="healthy">Healthy</option><option value="warning">Warning</option><option value="critical">Critical</option></select></div>
    </div>`, `<button class="btn btn-primary" onclick="StoragePage.submitDisk()">Create</button>`); }

    async function submitDisk() {
        const d = { server:parseInt(document.getElementById('dv-server').value), mount_point:document.getElementById('dv-mount').value.trim(), size:document.getElementById('dv-size').value.trim(), used:document.getElementById('dv-used').value.trim(), available:document.getElementById('dv-avail').value.trim(), health:document.getElementById('dv-health').value };
        if (!d.mount_point) return Toast.error('Mount point required.');
        try { await API.post('/api/system-admin/disk-volumes/', d); Toast.success('Disk volume created!'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); }
    }

    async function editDisk(id) {
        try { const d = await API.get('/api/system-admin/disk-volumes/'+id+'/');
        Modal.open(window.t('Edit Disk Volume'), `<div style="display:grid;gap:var(--space-4);">
            <div class="form-group"><label class="form-label">Server</label><select class="form-input" id="dv-server">${_srvOpts(d.server)}</select></div>
            <div class="form-group"><label class="form-label">Mount Point</label><input class="form-input" id="dv-mount" value="${d.mount_point}"></div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:var(--space-4);">
                <div class="form-group"><label class="form-label">Size</label><input class="form-input" id="dv-size" value="${d.size}"></div>
                <div class="form-group"><label class="form-label">Used</label><input class="form-input" id="dv-used" value="${d.used}"></div>
                <div class="form-group"><label class="form-label">Available</label><input class="form-input" id="dv-avail" value="${d.available}"></div>
            </div>
            <div class="form-group"><label class="form-label">Health</label><select class="form-input" id="dv-health"><option value="healthy" ${d.health==='healthy'?'selected':''}>Healthy</option><option value="warning" ${d.health==='warning'?'selected':''}>Warning</option><option value="critical" ${d.health==='critical'?'selected':''}>Critical</option></select></div>
        </div>`, `<button class="btn btn-primary" onclick="StoragePage.submitDiskEdit(${id})">Save</button>`);
        } catch(e) { Toast.error('Failed: '+e.message); }
    }
    async function submitDiskEdit(id) { const d={server:parseInt(document.getElementById('dv-server').value),mount_point:document.getElementById('dv-mount').value.trim(),size:document.getElementById('dv-size').value.trim(),used:document.getElementById('dv-used').value.trim(),available:document.getElementById('dv-avail').value.trim(),health:document.getElementById('dv-health').value}; try { await API.patch('/api/system-admin/disk-volumes/'+id+'/',d); Toast.success('Updated!'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    async function deleteDisk(id) { Modal.open(window.t('Delete'), `<p style="text-align:center;padding:16px;">Delete this disk volume?</p>`, `<button class="btn btn-outline" onclick="Modal.close()">Cancel</button><button class="btn" style="background:var(--clr-danger);color:white" onclick="StoragePage.confirmDeleteDisk(${id})">Delete</button>`); }
    async function confirmDeleteDisk(id) { try { await API.delete('/api/system-admin/disk-volumes/'+id+'/'); Toast.success('Deleted.'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }

    // LVM CRUD
    async function editLvm(id) {
        try { const l = await API.get('/api/system-admin/logical-volumes/'+id+'/');
        Modal.open(window.t('Edit Logical Volume'), `<div style="display:grid;gap:var(--space-4);">
            <div class="form-group"><label class="form-label">Server</label><select class="form-input" id="lv-server">${_srvOpts(l.server)}</select></div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4);">
                <div class="form-group"><label class="form-label">VG Name</label><input class="form-input" id="lv-vg" value="${l.vg_name}"></div>
                <div class="form-group"><label class="form-label">LV Name</label><input class="form-input" id="lv-lv" value="${l.lv_name}"></div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4);">
                <div class="form-group"><label class="form-label">Size</label><input class="form-input" id="lv-size" value="${l.size}"></div>
                <div class="form-group"><label class="form-label">Status</label><select class="form-input" id="lv-status"><option value="active" ${l.status==='active'?'selected':''}>Active</option><option value="inactive" ${l.status==='inactive'?'selected':''}>Inactive</option></select></div>
            </div>
        </div>`, `<button class="btn btn-primary" onclick="StoragePage.submitLvmEdit(${id})">Save</button>`);
        } catch(e) { Toast.error('Failed: '+e.message); }
    }
    async function submitLvmEdit(id) { const d={server:parseInt(document.getElementById('lv-server').value),vg_name:document.getElementById('lv-vg').value.trim(),lv_name:document.getElementById('lv-lv').value.trim(),size:document.getElementById('lv-size').value.trim(),status:document.getElementById('lv-status').value}; try { await API.patch('/api/system-admin/logical-volumes/'+id+'/',d); Toast.success('Updated!'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }
    async function deleteLvm(id) { Modal.open(window.t('Delete'), `<p style="text-align:center;padding:16px;">Delete this logical volume?</p>`, `<button class="btn btn-outline" onclick="Modal.close()">Cancel</button><button class="btn" style="background:var(--clr-danger);color:white" onclick="StoragePage.confirmDeleteLvm(${id})">Delete</button>`); }
    async function confirmDeleteLvm(id) { try { await API.delete('/api/system-admin/logical-volumes/'+id+'/'); Toast.success('Deleted.'); Modal.close(); loadData(); } catch(e) { Toast.error('Failed: '+e.message); } }

    return { render, loadData, openAddDiskModal, submitDisk, editDisk, submitDiskEdit, deleteDisk, confirmDeleteDisk, editLvm, submitLvmEdit, deleteLvm, confirmDeleteLvm };
})();
window.StoragePage = StoragePage;

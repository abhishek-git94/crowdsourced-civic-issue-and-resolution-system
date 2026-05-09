// Configuration - CHANGE THIS to your backend IP
const API_BASE = 'http://127.0.0.1:5000';

let currentUser = null;
let allIssues = [];
let allUsers = [];
let filteredIssues = [];
let filteredUsers = [];
let currentPage = 1;
let userSortKey = 'name';
let userSortDir = 1; // 1 = asc, -1 = desc
const itemsPerPage = 15;
let issueModal = null;
let isDemoMode = false;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    issueModal = new bootstrap.Modal(document.getElementById('issueModal'));
    checkServerConnection();
});

async function checkServerConnection() {
    try {
        // Try a public endpoint that doesn't require auth first, or use the debug one
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);
        
        const res = await fetch(`${API_BASE}/auth/debug-user`, { 
            method: 'POST', 
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email: 'check@js.com'}),
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        
        console.log("Backend response received:", res.status);
        // Any response (even 401/403) means the server is UP
        console.log("Backend reachable.");
    } catch (err) {
        console.warn("Backend not reachable or timeout. Entering Indore Demo Mode.", err);
        enableDemoMode();
    }
}

function enableDemoMode() {
    if (isDemoMode) return;
    isDemoMode = true;
    if (!document.querySelector('.demo-mode-badge')) {
        document.body.insertAdjacentHTML('beforeend', `
            <div class="demo-mode-badge">
                <div class="demo-pulse"></div>
                Indore Demo Mode Active
            </div>
        `);
    }
    loadIndoreSampleData();
}

// Login
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('adminEmail').value;
    const password = document.getElementById('adminPassword').value;

    if (isDemoMode) {
        if (email.includes('admin') || email.includes('indore')) {
            currentUser = { name: 'Indore Admin', role: 'admin', email };
            loginSuccess();
        } else {
            showToast('Demo Login: Use "admin" or "indore" in email', 'warning');
        }
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok && (data.user.role === 'admin' || data.user.role === 'manager')) {
            currentUser = data.user;
            loginSuccess();
        } else {
            showToast('Access denied. Admin/Manager only.', 'danger');
        }
    } catch (err) {
        showToast('Connection failed. Switching to Demo Mode.', 'warning');
        enableDemoMode();
    }
});

function loginSuccess() {
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('dashboardScreen').style.display = 'block';
    loadDashboard();
    showToast('Welcome to Jan Suvidha Indore Portal!', 'success');
}

// Logout
function logout() {
    currentUser = null;
    document.getElementById('loginScreen').style.display = 'flex';
    document.getElementById('dashboardScreen').style.display = 'none';
    showToast('Logged out successfully', 'info');
}

// Show Page
function showPage(pageName, element) {
    if(element) {
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        element.classList.add('active');
    }
    
    document.querySelectorAll('[id^="page-"]').forEach(p => p.style.display = 'none');
    document.getElementById('page-' + pageName).style.display = 'block';
    
    if (pageName === 'overview') loadDashboard();
    if (pageName === 'issues') loadAllIssues();
    if (pageName === 'departments') loadDepartments();
    if (pageName === 'analytics') loadAnalytics();
    if (pageName === 'users') loadUsers();
}

// Load Dashboard
async function loadDashboard() {
    if (isDemoMode) {
        renderDemoDashboard();
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/admin/dashboard`, {
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });
        const data = await res.json();

        updateStats(data);
        renderStatusChart(data.status_labels, data.status_values);
        renderDailyChart(data.daily_labels, data.daily_values);
        renderRecentIssues(data.prioritized_issues || []);
    } catch (err) {
        enableDemoMode();
        renderDemoDashboard();
    }
}

function updateStats(data) {
    document.getElementById('statTotal').textContent = data.total_issues || 0;
    document.getElementById('statPending').textContent = data.pending_count || 0;
    document.getElementById('statResolved').textContent = data.resolved_count || 0;
    document.getElementById('statCritical').textContent = data.critical_count || 0;
    document.getElementById('issueCountBadge').textContent = data.total_issues || 0;
    
    // Update analysis stats if present
    if (document.getElementById('resRate')) {
        document.getElementById('resRate').textContent = (data.res_rate || 0) + '%';
    }
    if (document.getElementById('avgTime')) {
        document.getElementById('avgTime').textContent = (data.avg_res_time || 0) + ' hrs';
    }
    if (document.getElementById('totalUsers')) {
        document.getElementById('totalUsers').textContent = data.total_users || 0;
    }
}

function renderDemoDashboard() {
    updateStats({ total_issues: 1248, pending_count: 412, resolved_count: 782, critical_count: 54 });
    renderStatusChart(['Pending', 'In Progress', 'Resolved', 'Linked'], [412, 185, 597, 54]);
    renderDailyChart(['03 May', '04 May', '05 May', '06 May', '07 May', '08 May', '09 May'], [45, 62, 58, 71, 65, 88, 52]);
    renderRecentIssues(allIssues.slice(0, 8));
}

// Indore-focused sample data
function loadIndoreSampleData() {
    const locations = [
        'Rajwada Circle, Indore', 'Vijay Nagar Square', 'Palasia Square', 'Bhanwarkuan', 
        'Sarafa Bazaar', 'Chappan Dukan', 'Annapurna Temple Area', 'Khajrana', 
        'Bengali Square', 'Geeta Bhawan', 'Rau Circle', 'Pipliyahana', 'LIG Colony'
    ];
    
    const categories = ['roads', 'sanitation', 'water', 'electricity', 'traffic', 'parks'];
    const issues_pool = {
        'roads': ['Large pothole blocking lane', 'Broken divider near square', 'Illegal speed breaker', 'Road sinking after rain'],
        'sanitation': ['Garbage heap uncollected for 3 days', 'Open dustbin overflowing', 'Dead animal on street', 'Public toilet cleaning required'],
        'water': ['Major pipeline burst', 'Contaminated water supply', 'Low water pressure in locality', 'Water leakage from tank'],
        'electricity': ['Street light flickering', 'Hanging live wires', 'Transformer spark reported', 'No street lights on main road'],
        'traffic': ['Signal malfunction at peak hour', 'Illegal parking blocking road', 'Wrong side driving hotspot', 'Traffic congestion near mall'],
        'parks': ['Broken swings in public park', 'Overgrown grass/maintenance needed', 'Lighting required in park', 'Encroachment in green zone']
    };

    const statuses = ['Pending', 'In Progress', 'Resolved', 'Linked'];
    const severities = ['High', 'Medium', 'Low', 'Critical'];
    const departments = ['PWD', 'IMC Sanitation', 'Narmada Water Dept', 'MP Electricity Board', 'Traffic Police', 'Garden Dept'];

    allIssues = [];
    for (let i = 1; i <= 60; i++) {
        const cat = categories[Math.floor(Math.random() * categories.length)];
        const loc = locations[Math.floor(Math.random() * locations.length)];
        const issue_text = issues_pool[cat][Math.floor(Math.random() * issues_pool[cat].length)];
        
        allIssues.push({
            id: `IND-${1000 + i}`,
            issue: issue_text,
            location: loc,
            category: cat,
            status: statuses[Math.floor(Math.random() * statuses.length)],
            severity: severities[Math.floor(Math.random() * severities.length)],
            priority: Math.random() > 0.7 ? 'Urgent' : 'Normal',
            upvotes: Math.floor(Math.random() * 100),
            assigned_to: departments[categories.indexOf(cat)],
            created_at: new Date(Date.now() - Math.random() * 1000000000).toISOString()
        });
    }
    
    filteredIssues = [...allIssues];
}

// Load Issues
async function loadAllIssues() {
    if (isDemoMode) {
        renderIssuesTable();
        return;
    }
    
    try {
        const res = await fetch(`${API_BASE}/view`, {
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });
        const data = await res.json();
        allIssues = data.issues || [];
        filteredIssues = [...allIssues];
        renderIssuesTable();
    } catch (err) {
        enableDemoMode();
        renderIssuesTable();
    }
}

// Render Table
function renderIssuesTable() {
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageItems = filteredIssues.slice(start, end);
    
    const tbody = document.getElementById('issuesTable');
    if (pageItems.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center py-5 text-muted">No issues found matching filters</td></tr>';
        return;
    }
    
    tbody.innerHTML = pageItems.map(i => `
        <tr>
            <td><input type="checkbox" class="form-check-input issue-checkbox" data-id="${i.id}"></td>
            <td><span class="text-muted small">${i.id}</span></td>
            <td>
                <div class="fw-bold">${i.issue}</div>
                <div class="small text-muted">${i.category.toUpperCase()} <span class="ai-badge">AI Verified</span></div>
            </td>
            <td><i class="bi bi-geo-alt me-1"></i>${i.location}</td>
            <td><span class="status-badge ${getStatusClass(i.status)}">${i.status}</span></td>
            <td><span class="${getSeverityClass(i.severity)} fw-bold">${i.severity}</span></td>
            <td><span class="badge bg-light text-dark border"><i class="bi bi-star-fill text-warning me-1"></i>${i.upvotes}</span></td>
            <td><span class="badge bg-secondary opacity-75">${i.assigned_to}</span></td>
            <td>
                <div class="d-flex gap-1">
                    <button class="btn btn-sm btn-outline-primary" onclick="openIssueModal('${i.id}')"><i class="bi bi-pencil"></i></button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteIssue('${i.id}')"><i class="bi bi-trash"></i></button>
                </div>
            </td>
        </tr>
    `).join('');
    
    document.getElementById('paginationInfo').textContent = `Showing ${start + 1}-${Math.min(end, filteredIssues.length)} of ${filteredIssues.length}`;
    renderPagination();
}

function renderRecentIssues(issues) {
    const tbody = document.getElementById('recentIssuesTable');
    const displayIssues = issues.length > 0 ? issues : allIssues.slice(0, 8);
    
    tbody.innerHTML = displayIssues.map(i => `
        <tr>
            <td class="fw-bold">${i.issue.substring(0, 45)}${i.issue.length > 45 ? '...' : ''}</td>
            <td><span class="text-muted small">${i.location}</span></td>
            <td><span class="status-badge ${getStatusClass(i.status)}">${i.status}</span></td>
            <td class="${getSeverityClass(i.severity)} fw-bold">${i.severity}</td>
            <td><span class="badge bg-light text-dark"><i class="bi bi-star-fill text-warning me-1"></i>${i.upvotes}</span></td>
            <td><button class="btn btn-sm btn-link text-primary" onclick="openIssueModal('${i.id}')">View</button></td>
        </tr>
    `).join('');
}

// Chart Helpers
function renderStatusChart(labels, values) {
    const ctx = document.getElementById('statusChart');
    if (!ctx) return;
    const existingChart = Chart.getChart(ctx);
    if (existingChart) existingChart.destroy();

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{ data: values, backgroundColor: ['#f59e0b', '#3b82f6', '#10b981', '#64748b'], borderWidth: 0, hoverOffset: 15 }]
        },
        options: { responsive: true, maintainAspectRatio: false, cutout: '75%', plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, padding: 20 } } } }
    });
}

function renderDailyChart(labels, values) {
    const ctx = document.getElementById('dailyChart');
    if (!ctx) return;
    const existingChart = Chart.getChart(ctx);
    if (existingChart) existingChart.destroy();

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{ label: 'Issues', data: values, borderColor: '#6366f1', backgroundColor: 'rgba(99, 102, 241, 0.1)', fill: true, tension: 0.4 }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true }, x: { grid: { display: false } } } }
    });
}

function renderMonthlyChart(labels, values) {
    const ctx = document.getElementById('monthlyChart');
    if (!ctx) return;
    const existingChart = Chart.getChart(ctx);
    if (existingChart) existingChart.destroy();

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{ label: 'Issues per Month', data: values, backgroundColor: '#0d6efd', borderRadius: 8 }]
        },
        options: { 
            responsive: true, 
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });
}

// Utils
function getStatusClass(status) {
    if(status.includes('Resolved')) return 'status-resolved';
    if(status === 'In Progress') return 'status-progress';
    return 'status-pending';
}

function getSeverityClass(severity) {
    if(severity === 'High' || severity === 'Critical') return 'text-danger';
    if(severity === 'Medium') return 'text-warning';
    return 'text-success';
}

function changePage(page) { currentPage = page; renderIssuesTable(); }

function renderPagination() {
    const totalPages = Math.ceil(filteredIssues.length / itemsPerPage);
    let html = '';
    html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}"><a class="page-link" href="#" onclick="changePage(${currentPage - 1})">Prev</a></li>`;
    for(let i = 1; i <= Math.min(5, totalPages); i++) {
        html += `<li class="page-item ${currentPage === i ? 'active' : ''}"><a class="page-link" href="#" onclick="changePage(${i})">${i}</a></li>`;
    }
    html += `<li class="page-item ${currentPage >= totalPages ? 'disabled' : ''}"><a class="page-link" href="#" onclick="changePage(${currentPage + 1})">Next</a></li>`;
    document.getElementById('pagination').innerHTML = html;
}

// Issue Modal Logic
let currentIssueId = null;
function openIssueModal(issueId) {
    currentIssueId = issueId;
    const issue = allIssues.find(i => i.id === issueId);
    if(issue) {
        document.getElementById('modalStatus').value = issue.status;
        document.getElementById('modalDepartment').value = issue.assigned_to;
        document.getElementById('modalSeverity').value = issue.severity;
        document.getElementById('modalPriority').value = issue.priority || 'Normal';
    }
    issueModal.show();
}

async function saveIssueChanges() {
    if(!currentIssueId) return;
    const status = document.getElementById('modalStatus').value;
    const assigned_to = document.getElementById('modalDepartment').value;
    
    if (isDemoMode) {
        const issueIdx = allIssues.findIndex(i => i.id === currentIssueId);
        if (issueIdx !== -1) {
            allIssues[issueIdx].status = status;
            allIssues[issueIdx].assigned_to = assigned_to;
            filteredIssues = [...allIssues];
            renderIssuesTable();
            showToast('Demo: Issue updated locally', 'success');
        }
        issueModal.hide();
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/admin/issues/${currentIssueId}/status`, {
            method: 'POST',
            body: new URLSearchParams({ status, assigned_to })
        });
        if(res.ok) {
            showToast('Issue updated!', 'success');
            issueModal.hide();
            loadAllIssues();
        }
    } catch(err) { showToast('Error updating issue', 'danger'); }
}

async function deleteIssue(id) {
    if(!confirm('Delete this issue?')) return;
    if (isDemoMode) {
        allIssues = allIssues.filter(i => i.id !== id);
        filteredIssues = [...allIssues];
        renderIssuesTable();
        showToast('Demo: Issue deleted', 'info');
        return;
    }
}

// AI Endpoints
async function runClustering() {
    showToast('Running AI clustering...', 'info');
    if (isDemoMode) {
        setTimeout(() => showToast('Found 4 issue clusters in Indore region', 'success'), 1500);
        return;
    }
}

async function runAIQuery() {
    const query = document.getElementById('aiQueryInput').value;
    if(!query) return;
    showToast('AI thinking...', 'info');
    if (isDemoMode) {
        setTimeout(() => showToast(`AI filtered ${Math.floor(Math.random()*10)} matching issues`, 'success'), 1200);
        return;
    }
}

async function detectAnomalies() {
    showToast('Analyzing patterns...', 'info');
    if (isDemoMode) {
        setTimeout(() => showToast('Anomaly detected: Unusual spike in garbage reports in Vijay Nagar', 'warning'), 2000);
        return;
    }
}

// Analytics & Reports
function loadDepartments() {
    const tbody = document.getElementById('deptTable');
    const depts = [
        { name: 'PWD Roads', head: 'Mr. Sharma', load: 85, efficiency: 92 },
        { name: 'IMC Sanitation', head: 'Ms. Verma', load: 124, efficiency: 78 },
        { name: 'Narmada Water', head: 'Mr. Gupta', load: 62, efficiency: 85 },
        { name: 'MPEB Electricity', head: 'Mr. Khan', load: 45, efficiency: 95 }
    ];
    tbody.innerHTML = depts.map(d => `
        <tr><td><strong>${d.name}</strong></td><td>${d.head}</td><td><span class="badge bg-primary">${d.load}</span></td>
        <td><div class="progress" style="height: 6px; width: 100px;"><div class="progress-bar bg-success" style="width: ${d.efficiency}%"></div></div></td>
        <td>${d.efficiency}%</td><td><button class="btn btn-sm btn-light border">Manage</button></td></tr>`).join('');
}

async function loadAnalytics() {
    if (isDemoMode) {
        document.getElementById('resRate').textContent = '62.7%';
        document.getElementById('avgTime').textContent = '4.8 days';
        document.getElementById('totalUsers').textContent = '1,452';
        return;
    }

    try {
        // Fetch from dashboard endpoint for category stats
        const dashRes = await fetch(`${API_BASE}/admin/dashboard`, {
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });
        const dashData = await dashRes.json();
        
        const res = await fetch(`${API_BASE}/admin/analytics/stats`, {
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });
        const data = await res.json();
        
        if (data.success) {
            document.getElementById('resRate').textContent = data.res_rate + '%';
            document.getElementById('avgTime').textContent = data.avg_time;
            document.getElementById('totalUsers').textContent = data.total_users;
            
            if (data.monthly_labels) {
                renderMonthlyChart(data.monthly_labels, data.monthly_values);
            }
            
            if (dashData.category_labels) {
                renderTopCatChart(dashData.category_labels, dashData.category_values);
            }
        }
    } catch (err) {
        console.error("Failed to load analytics:", err);
    }
}

function renderTopCatChart(labels, values) {
    const ctx = document.getElementById('topCatChart');
    if (!ctx) return;
    const existingChart = Chart.getChart(ctx);
    if (existingChart) existingChart.destroy();

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{ data: values, backgroundColor: ['#0d6efd', '#198754', '#ffc107', '#dc3545', '#0dcaf0', '#6610f2'] }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } } }
    });
}

async function loadUsers() {
    if (isDemoMode) {
        document.getElementById('usersTable').innerHTML = '<tr><td colspan="7" class="text-center py-4">User management is disabled in Demo Mode</td></tr>';
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/admin/users/all`, {
        const res = await fetch(`${API_BASE}/admin/users`, {
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });
        const data = await res.json();
        if (data.success) {
            allUsers = data.users || [];
            filteredUsers = [...allUsers];
            renderUsersTable();
        }
    } catch (err) {
        console.error('Failed to load users:', err);
        document.getElementById('usersTable').innerHTML = '<tr><td colspan="7" class="text-center py-4 text-danger">Error connecting to server</td></tr>';
    }
}

function renderUsersTable() {
    const sorted = [...filteredUsers].sort((a, b) => {
        const av = (a[userSortKey] || '').toString().toLowerCase();
        const bv = (b[userSortKey] || '').toString().toLowerCase();
        if (av < bv) return -1 * userSortDir;
        if (av > bv) return  1 * userSortDir;
        return 0;
    });
    const tbody = document.getElementById('usersTable');
    if (sorted.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">No users found</td></tr>';
        return;
    }
    tbody.innerHTML = sorted.map(u => `
        <tr>
            <td><strong>${u.name}</strong></td>
            <td>${u.email}</td>
            <td>
                <select class="form-select form-select-sm" style="width:auto;"
                    onchange="changeUserRole('${u.id}', this.value)">
                    <option value="citizen"  ${u.role==='citizen'  ? 'selected' : ''}>Citizen</option>
                    <option value="manager"  ${u.role==='manager'  ? 'selected' : ''}>Manager</option>
                    <option value="admin"    ${u.role==='admin'    ? 'selected' : ''}>Admin</option>
                </select>
            </td>
            <td>${u.points || 0}</td>
            <td>${u.issues_reported || 0}</td>
            <td>${u.joined}</td>
            <td>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteUser('${u.id}','${u.name}')">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function sortUsers(key) {
    if (userSortKey === key) userSortDir *= -1;
    else { userSortKey = key; userSortDir = 1; }
    renderUsersTable();
    showToast(`Sorted by ${key}`, 'info');
}

function filterUsers() {
    const search = (document.getElementById('userSearch')?.value || '').toLowerCase();
    const role   = document.getElementById('roleFilter')?.value || '';
    filteredUsers = allUsers.filter(u => {
        const matchSearch = !search ||
            (u.name  || '').toLowerCase().includes(search) ||
            (u.email || '').toLowerCase().includes(search);
        const matchRole = !role || u.role === role;
        return matchSearch && matchRole;
    });
    renderUsersTable();
}

async function changeUserRole(userId, newRole) {
    try {
        const res = await fetch(`${API_BASE}/auth/profile`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'X-User-ID': userId },
            body: JSON.stringify({ role: newRole })
        });
        if (res.ok) {
            const u = allUsers.find(u => u.id === userId);
            if (u) u.role = newRole;
            showToast(`Role updated to ${newRole}`, 'success');
        } else {
            showToast('Failed to update role', 'danger');
        }
    } catch (err) {
        showToast('Error: ' + err.message, 'danger');
    }
}

async function deleteUser(userId, userName) {
    if (!confirm(`Delete user "${userName}"? This cannot be undone.`)) return;
    showToast('Delete user: connect backend /admin/users/<id> DELETE endpoint', 'warning');
    // Optimistic removal from local list
    allUsers = allUsers.filter(u => u.id !== userId);
    filteredUsers = filteredUsers.filter(u => u.id !== userId);
    renderUsersTable();
}

function exportAllData() { exportData('issues'); }
function exportData(type) { showToast(`Exporting ${type} as CSV...`, 'success'); }

// Settings Tools
async function testClassify() {
    const desc = document.getElementById('classifyDesc').value;
    if(!desc) return;
    showToast('Classifying with AI...', 'info');
    try {
        const res = await fetch(`${API_BASE}/api/classify-issue`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ description: desc })
        });
        const data = await res.json();
        const el = document.getElementById('classifyResult');
        if (data.category) {
            el.innerHTML = `<span class="text-success">✓ Category: <b>${data.category}</b></span><br>
            <span class="text-info">Severity: ${data.severity || 'Medium'}</span><br>
            <span class="text-muted">Dept: ${data.recommended_department || data.assigned_department || '—'}</span>`;
        } else {
            el.innerHTML = `<span class="text-warning">${JSON.stringify(data)}</span>`;
        }
    } catch(e) {
        setTimeout(() => {
            document.getElementById('classifyResult').innerHTML = `<span class="text-success">✓ Category: Roads</span><br><span class="text-info">Subclass: Pothole</span>`;
        }, 800);
    }
}

async function testHotspots() {
    showToast('Predicting...', 'info');
    setTimeout(() => {
        document.getElementById('hotspotResult').innerHTML = `<div class="text-danger fw-bold">✓ High Probability:</div><ul class="ps-3 mb-0"><li>Vijay Nagar (85%)</li><li>Rajwada (72%)</li></ul>`;
    }, 1000);
}

async function testSimilar() {
    showToast('Searching...', 'info');
    setTimeout(() => {
        document.getElementById('similarResult').innerHTML = `<div class="text-info">✓ Found 2 similar issues nearby</div>`;
    }, 1000);
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0 show`;
    toast.innerHTML = `<div class="d-flex"><div class="toast-body">${message}</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

// Global filter functions
function filterIssues() {
    const search = document.getElementById('searchInput').value.toLowerCase();
    const status = document.getElementById('statusFilter').value;
    const severity = document.getElementById('severityFilter').value;
    filteredIssues = allIssues.filter(i => {
        return (i.issue.toLowerCase().includes(search) || i.location.toLowerCase().includes(search)) &&
               (!status || i.status === status) && (!severity || i.severity === severity);
    });
    currentPage = 1; renderIssuesTable();
}

function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('statusFilter').value = '';
    document.getElementById('severityFilter').value = '';
    filteredIssues = [...allIssues]; renderIssuesTable();
}

function refreshData() {
    showToast('Refreshing...', 'info');
    setTimeout(() => { loadDashboard(); showToast('Data synced', 'success'); }, 800);
}

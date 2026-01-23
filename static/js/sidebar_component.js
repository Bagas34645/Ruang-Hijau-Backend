// sidebar_component.js - Komponen sidebar yang bisa dipakai di semua halaman admin

function initSidebar(activePage) {
    const sidebarHTML = `
        <div class="sidebar">
            <div class="sidebar-header">
                <h1>🌿 RuangHijau Admin</h1>
            </div>
            <div class="sidebar-menu">
                <a class="menu-item ${activePage === 'dashboard' ? 'active' : ''}" href="/admin">
                    <i class="fas fa-home"></i>
                    <span>Dashboard</span>
                </a>
                <a class="menu-item ${activePage === 'users' ? 'active' : ''}" href="/admin/users">
                    <i class="fas fa-users"></i>
                    <span>Manajemen Pengguna</span>
                </a>
                <a class="menu-item ${activePage === 'posts' ? 'active' : ''}" href="/admin/posts">
                    <i class="fas fa-file-alt"></i>
                    <span>Postingan & Komentar</span>
                </a>
                <a class="menu-item ${activePage === 'campaigns' ? 'active' : ''}" href="/admin/campaigns">
                    <i class="fas fa-bullhorn"></i>
                    <span>Kampanye</span>
                </a>
                <a class="menu-item ${activePage === 'donations' ? 'active' : ''}" href="/admin/donations">
                    <i class="fas fa-dollar-sign"></i>
                    <span>Donasi</span>
                </a>
                <a class="menu-item ${activePage === 'volunteers' ? 'active' : ''}" href="/admin/volunteers">
                    <i class="fas fa-hands-helping"></i>
                    <span>Volunteer</span>
                </a>
                <a class="menu-item ${activePage === 'feedback' ? 'active' : ''}" href="/admin/feedback">
                    <i class="fas fa-comment-dots"></i>
                    <span>Feedback</span>
                </a>
            </div>
            <div class="sidebar-footer">
                <div class="admin-profile">
                    <i class="fas fa-user-circle"></i>
                    <div class="admin-info">
                        <div class="admin-name" id="adminName">Admin</div>
                        <div class="admin-role">Administrator</div>
                    </div>
                </div>
                <button class="logout-btn" onclick="handleLogout()">
                    <i class="fas fa-sign-out-alt"></i>
                    <span>Logout</span>
                </button>
            </div>
        </div>
    `;
    
    // Insert sidebar at the beginning of body
    document.body.insertAdjacentHTML('afterbegin', sidebarHTML);
    
    // Load admin info
    loadAdminInfo();
}

function loadAdminInfo() {
    const adminData = localStorage.getItem('adminData');
    if (adminData) {
        try {
            const admin = JSON.parse(adminData);
            const nameElement = document.getElementById('adminName');
            if (nameElement) {
                nameElement.textContent = admin.name || 'Admin';
            }
        } catch (e) {
            console.error('Error parsing admin data:', e);
        }
    }
}

function handleLogout() {
    if (confirm('Yakin ingin logout?')) {
        // Clear session data
        localStorage.removeItem('adminToken');
        localStorage.removeItem('adminData');
        sessionStorage.clear();
        
        // Redirect to login
        window.location.href = '/admin/login';
    }
}

// Check authentication on page load
function checkAuth() {
    const token = localStorage.getItem('adminToken');
    const currentPath = window.location.pathname;
    
    // If not logged in and not on login page, redirect to login
    if (!token && currentPath !== '/admin/login') {
        window.location.href = '/admin/login';
        return false;
    }
    
    // If logged in and on login page, redirect to dashboard
    if (token && currentPath === '/admin/login') {
        window.location.href = '/admin';
        return false;
    }
    
    return true;
}

// Add common styles for sidebar
const sidebarStyles = `
    <style>
        .sidebar-footer {
            padding: 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        .admin-profile {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            margin-bottom: 12px;
        }
        .admin-profile i {
            font-size: 32px;
            color: white;
        }
        .admin-info {
            flex: 1;
        }
        .admin-name {
            font-weight: 600;
            font-size: 14px;
            color: white;
        }
        .admin-role {
            font-size: 12px;
            color: rgba(255,255,255,0.7);
        }
        .logout-btn {
            width: 100%;
            padding: 12px;
            background: rgba(220, 38, 38, 0.9);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.3s;
        }
        .logout-btn:hover {
            background: rgba(220, 38, 38, 1);
        }
    </style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', sidebarStyles);
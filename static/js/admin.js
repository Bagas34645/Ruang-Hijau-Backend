// Admin Dashboard JavaScript
// NOTE: admin blueprint terdaftar di /admin (bukan /api/admin)
const ADMIN_API_BASE = '/admin';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function () {
    checkAuth();
    initializeNavigation();
    initializeMenuToggle();
    initializeLogout();
    loadDashboard();
});

// Check authentication
async function checkAuth() {
    try {
        const response = await fetch('/admin/check-auth');
        if (!response.ok) {
            window.location.href = '/admin/login';
            return;
        }
        const data = await response.json();
        if (data.user) {
            updateUserInfo(data.user);
        }
    } catch (error) {
        console.error('Auth check error:', error);
        window.location.href = '/admin/login';
    }
}

// Update user info in sidebar
function updateUserInfo(user) {
    const userName = document.getElementById('userName');
    const userEmail = document.getElementById('userEmail');
    const userInitial = document.getElementById('userInitial');

    if (userName) userName.textContent = user.name || 'Admin';
    if (userEmail) userEmail.textContent = user.email || '';
    if (userInitial) userInitial.textContent = (user.name || 'A').charAt(0).toUpperCase();
}

// Initialize navigation
function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            const section = this.getAttribute('data-section');
            switchSection(section);
        });
    });
}

// Switch between sections
function switchSection(section) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-section') === section) {
            item.classList.add('active');
        }
    });

    // Update content sections
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.classList.remove('active');
    });

    const targetSection = document.getElementById(`${section}-section`);
    if (targetSection) {
        targetSection.classList.add('active');

        // Update page title
        const titles = {
            'dashboard': 'Dashboard',
            'users': 'Manajemen Pengguna',
            'posts': 'Manajemen Postingan',
            'campaigns': 'Manajemen Kampanye',
            'donations': 'Manajemen Donasi',
            'comments': 'Manajemen Komentar',
            'volunteers': 'Manajemen Relawan',
            'notifications': 'Manajemen Notifikasi',
            'likes': 'Analitik Likes',
            'feedback': 'Kelola Feedback & Analisis Sentimen'
        };
        document.getElementById('pageTitle').textContent = titles[section] || 'Dashboard';

        // Load section data
        loadSectionData(section);
    }
}

// Load section data
function loadSectionData(section) {
    switch (section) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'users':
            loadUsers();
            break;
        case 'posts':
            loadPosts();
            break;
        case 'campaigns':
            loadCampaigns();
            break;
        case 'donations':
            loadDonations();
            break;
        case 'comments':
            loadComments();
            break;
        case 'volunteers':
            loadVolunteers();
            break;
        case 'notifications':
            loadNotifications();
            break;
        case 'likes':
            loadLikes();
            break;
        case 'feedback':
            // Feedback is handled by feedback_dashboard.js
            if (typeof initFeedbackDashboard === 'function') {
                initFeedbackDashboard();
            }
            break;
    }
}

// Load dashboard statistics
async function loadDashboard() {
    try {
        // Load stats
        const [
            usersRes,
            postsRes,
            campaignsRes,
            donationsRes,
            commentsRes,
            volunteersRes,
            notifUnreadRes
        ] = await Promise.all([
            fetch(`${ADMIN_API_BASE}/stats/users`),
            fetch(`${ADMIN_API_BASE}/stats/posts`),
            fetch(`${ADMIN_API_BASE}/stats/campaigns`),
            fetch(`${ADMIN_API_BASE}/stats/donations`),
            fetch(`${ADMIN_API_BASE}/stats/comments`),
            fetch(`${ADMIN_API_BASE}/stats/volunteers`),
            fetch(`${ADMIN_API_BASE}/stats/notifications-unread`)
        ]);

        const usersData = await usersRes.json();
        const postsData = await postsRes.json();
        const campaignsData = await campaignsRes.json();
        const donationsData = await donationsRes.json();
        const commentsData = await commentsRes.json();
        const volunteersData = await volunteersRes.json();
        const notifUnreadData = await notifUnreadRes.json();

        document.getElementById('totalUsers').textContent = usersData.count || 0;
        document.getElementById('totalPosts').textContent = postsData.count || 0;
        document.getElementById('totalCampaigns').textContent = campaignsData.count || 0;

        const totalDonations = donationsData.total || 0;
        document.getElementById('totalDonations').textContent = formatCurrency(totalDonations);

        const totalCommentsEl = document.getElementById('totalComments');
        const totalVolunteersEl = document.getElementById('totalVolunteers');
        const unreadNotificationsEl = document.getElementById('unreadNotifications');
        if (totalCommentsEl) totalCommentsEl.textContent = commentsData.count || 0;
        if (totalVolunteersEl) totalVolunteersEl.textContent = volunteersData.count || 0;
        if (unreadNotificationsEl) unreadNotificationsEl.textContent = notifUnreadData.count || 0;

        // Load recent activity
        loadRecentActivity();

        // Load monthly stats
        loadMonthlyStats();
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Load recent activity
async function loadRecentActivity() {
    try {
        const response = await fetch(`${ADMIN_API_BASE}/recent-activity`);
        const data = await response.json();

        const container = document.getElementById('recentActivity');
        if (data.activities && data.activities.length > 0) {
            container.innerHTML = data.activities.map(activity => `
                <div class="activity-item">
                    <div class="activity-icon" style="background: ${getActivityColor(activity.type)}">
                        ${getActivityIcon(activity.type)}
                    </div>
                    <div class="activity-content">
                        <div class="activity-title">${activity.title}</div>
                        <div class="activity-time">${formatTime(activity.created_at)}</div>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p style="color: var(--gray); text-align: center;">Tidak ada aktivitas terbaru</p>';
        }
    } catch (error) {
        console.error('Error loading recent activity:', error);
        document.getElementById('recentActivity').innerHTML = '<p style="color: var(--danger);">Gagal memuat aktivitas</p>';
    }
}

// Load monthly stats
async function loadMonthlyStats() {
    try {
        const response = await fetch(`${ADMIN_API_BASE}/monthly-stats`);
        const data = await response.json();

        const container = document.getElementById('monthlyStats');
        if (data.stats) {
            container.innerHTML = Object.entries(data.stats).map(([key, value]) => `
                <div class="stat-row">
                    <span class="stat-label">${key}</span>
                    <span class="stat-value">${typeof value === 'number' && key.includes('Donasi') ? formatCurrency(value) : value}</span>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p style="color: var(--gray); text-align: center;">Tidak ada data</p>';
        }
    } catch (error) {
        console.error('Error loading monthly stats:', error);
        document.getElementById('monthlyStats').innerHTML = '<p style="color: var(--danger);">Gagal memuat statistik</p>';
    }
}

// Load users
async function loadUsers() {
    try {
        const response = await fetch(`${ADMIN_API_BASE}/users`);
        const data = await response.json();

        const tbody = document.getElementById('usersTableBody');
        if (data.users && data.users.length > 0) {
            tbody.innerHTML = data.users.map(user => `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.name}</td>
                    <td>${user.email}</td>
                    <td><span class="badge ${user.role === 'admin' ? 'badge-admin' : 'badge-user'}">${user.role}</span></td>
                    <td>${formatDate(user.created_at)}</td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="updateUserRole(${user.id}, '${String(user.role || 'user').replace(/'/g, "\\'")}')">Ubah Role</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id})">Hapus</button>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">Tidak ada data pengguna</td></tr>';
        }
    } catch (error) {
        console.error('Error loading users:', error);
        document.getElementById('usersTableBody').innerHTML = '<tr><td colspan="6" class="loading" style="color: var(--danger);">Gagal memuat data</td></tr>';
    }
}

// Load posts
async function loadPosts() {
    try {
        const response = await fetch(`${ADMIN_API_BASE}/posts`);
        const data = await response.json();

        const tbody = document.getElementById('postsTableBody');
        if (data.posts && data.posts.length > 0) {
            tbody.innerHTML = data.posts.map(post => `
                <tr>
                    <td>${post.id}</td>
                    <td>${post.user_name || 'Unknown'}</td>
                    <td class="text-truncate">${post.text || '-'}</td>
                    <td>${post.likes || 0}</td>
                    <td>${formatDate(post.created_at)}</td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="viewPost(${post.id})">Lihat</button>
                        <button class="btn btn-sm btn-danger" onclick="deletePost(${post.id})">Hapus</button>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">Tidak ada data postingan</td></tr>';
        }
    } catch (error) {
        console.error('Error loading posts:', error);
        document.getElementById('postsTableBody').innerHTML = '<tr><td colspan="6" class="loading" style="color: var(--danger);">Gagal memuat data</td></tr>';
    }
}

// Load campaigns
async function loadCampaigns() {
    try {
        const response = await fetch(`${ADMIN_API_BASE}/campaigns`);
        const data = await response.json();

        const tbody = document.getElementById('campaignsTableBody');
        if (data.campaigns && data.campaigns.length > 0) {
            tbody.innerHTML = data.campaigns.map(campaign => `
                <tr>
                    <td>${campaign.id}</td>
                    <td>${campaign.title}</td>
                    <td>${campaign.category || '-'}</td>
                    <td>${formatCurrency(campaign.target_amount || 0)}</td>
                    <td>${formatCurrency(campaign.current_amount || 0)}</td>
                    <td><span class="badge badge-${getStatusBadge(campaign.campaign_status)}">${campaign.campaign_status || 'active'}</span></td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="updateCampaignStatus(${campaign.id}, '${String(campaign.campaign_status || 'active').replace(/'/g, "\\'")}')">Update Status</button>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="7" class="loading">Tidak ada data kampanye</td></tr>';
        }
    } catch (error) {
        console.error('Error loading campaigns:', error);
        document.getElementById('campaignsTableBody').innerHTML = '<tr><td colspan="7" class="loading" style="color: var(--danger);">Gagal memuat data</td></tr>';
    }
}

// Load donations
async function loadDonations() {
    try {
        const response = await fetch(`${ADMIN_API_BASE}/donations`);
        const data = await response.json();

        const tbody = document.getElementById('donationsTableBody');
        if (data.donations && data.donations.length > 0) {
            tbody.innerHTML = data.donations.map(donation => `
                <tr>
                    <td>${donation.id}</td>
                    <td>${donation.user_name || 'Unknown'}</td>
                    <td>${donation.campaign_title || '-'}</td>
                    <td>${formatCurrency(donation.amount || 0)}</td>
                    <td>${formatDate(donation.created_at)}</td>
                    <td><span class="badge badge-${getStatusBadge(donation.status)}">${donation.status || 'pending'}</span></td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="updateDonationStatus(${donation.id}, '${String(donation.status || 'pending').replace(/'/g, "\\'")}')">Update Status</button>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="7" class="loading">Tidak ada data donasi</td></tr>';
        }
    } catch (error) {
        console.error('Error loading donations:', error);
        document.getElementById('donationsTableBody').innerHTML = '<tr><td colspan="7" class="loading" style="color: var(--danger);">Gagal memuat data</td></tr>';
    }
}

// Load comments
async function loadComments() {
    try {
        const response = await fetch(`${ADMIN_API_BASE}/comments`);
        const data = await response.json();

        const tbody = document.getElementById('commentsTableBody');
        if (data.comments && data.comments.length > 0) {
            tbody.innerHTML = data.comments.map(comment => `
                <tr>
                    <td>${comment.id}</td>
                    <td>${comment.post_id}</td>
                    <td>${comment.user_name || 'Unknown'}</td>
                    <td class="text-truncate">${comment.text || '-'}</td>
                    <td>${formatDate(comment.created_at)}</td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="deleteComment(${comment.id})">Hapus</button>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">Tidak ada data komentar</td></tr>';
        }
    } catch (error) {
        console.error('Error loading comments:', error);
        document.getElementById('commentsTableBody').innerHTML = '<tr><td colspan="6" class="loading" style="color: var(--danger);">Gagal memuat data</td></tr>';
    }
}

// Load volunteers
async function loadVolunteers() {
    try {
        const response = await fetch(`${ADMIN_API_BASE}/volunteers`);
        const data = await response.json();

        const tbody = document.getElementById('volunteersTableBody');
        if (data.volunteers && data.volunteers.length > 0) {
            tbody.innerHTML = data.volunteers.map(v => `
                <tr>
                    <td>${v.id}</td>
                    <td>${v.campaign_title || '-'}</td>
                    <td>${v.user_name || 'Unknown'}</td>
                    <td><span class="badge badge-${getStatusBadge(v.volunteer_status)}">${v.volunteer_status || 'applied'}</span></td>
                    <td>${typeof v.hours_contributed === 'number' ? v.hours_contributed : (v.hours_contributed || 0)}</td>
                    <td>${formatDate(v.created_at)}</td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="updateVolunteer(${v.id}, '${String(v.volunteer_status || 'applied').replace(/'/g, "\\'")}', ${Number(v.hours_contributed || 0)})">Update</button>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="7" class="loading">Tidak ada data relawan</td></tr>';
        }
    } catch (error) {
        console.error('Error loading volunteers:', error);
        document.getElementById('volunteersTableBody').innerHTML = '<tr><td colspan="7" class="loading" style="color: var(--danger);">Gagal memuat data</td></tr>';
    }
}

// Load notifications
async function loadNotifications() {
    try {
        const response = await fetch(`${ADMIN_API_BASE}/notifications`);
        const data = await response.json();

        const tbody = document.getElementById('notificationsTableBody');
        if (data.notifications && data.notifications.length > 0) {
            tbody.innerHTML = data.notifications.map(n => `
                <tr>
                    <td>${n.id}</td>
                    <td>${n.user_name || 'Unknown'}</td>
                    <td>${n.title || '-'}</td>
                    <td>${n.notification_type || '-'}</td>
                    <td><span class="badge ${n.is_read ? 'badge-success' : 'badge-warning'}">${n.is_read ? 'read' : 'unread'}</span></td>
                    <td>${formatDate(n.created_at)}</td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="deleteNotification(${n.id})">Hapus</button>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="7" class="loading">Tidak ada data notifikasi</td></tr>';
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
        document.getElementById('notificationsTableBody').innerHTML = '<tr><td colspan="7" class="loading" style="color: var(--danger);">Gagal memuat data</td></tr>';
    }
}

// Load likes analytics
async function loadLikes() {
    try {
        const response = await fetch(`${ADMIN_API_BASE}/likes/top-posts`);
        const data = await response.json();

        const tbody = document.getElementById('likesTableBody');
        if (data.posts && data.posts.length > 0) {
            tbody.innerHTML = data.posts.map(p => `
                <tr>
                    <td>${p.post_id}</td>
                    <td>${p.user_name || 'Unknown'}</td>
                    <td class="text-truncate">${p.text || '-'}</td>
                    <td>${p.likes_count || 0}</td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="4" class="loading">Tidak ada data</td></tr>';
        }
    } catch (error) {
        console.error('Error loading likes:', error);
        document.getElementById('likesTableBody').innerHTML = '<tr><td colspan="4" class="loading" style="color: var(--danger);">Gagal memuat data</td></tr>';
    }
}

// Menu toggle for mobile
function initializeMenuToggle() {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');

    if (menuToggle) {
        menuToggle.addEventListener('click', function () {
            sidebar.classList.toggle('open');
        });
    }
}

// Logout
function initializeLogout() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async function () {
            if (confirm('Apakah Anda yakin ingin keluar?')) {
                try {
                    await fetch('/admin/logout', { method: 'POST' });
                    window.location.href = '/admin/login';
                } catch (error) {
                    console.error('Logout error:', error);
                    window.location.href = '/admin/login';
                }
            }
        });
    }
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('id-ID', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Baru saja';
    if (minutes < 60) return `${minutes} menit yang lalu`;
    if (hours < 24) return `${hours} jam yang lalu`;
    if (days < 7) return `${days} hari yang lalu`;
    return formatDate(dateString);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0
    }).format(amount);
}

function getStatusBadge(status) {
    const statusMap = {
        'active': 'success',
        'completed': 'success',
        'pending': 'warning',
        'cancelled': 'danger',
        'rejected': 'danger',
        'failed': 'danger',
        'refunded': 'warning',
        'applied': 'warning',
        'accepted': 'success',
        'upcoming': 'info',
        'ongoing': 'warning'
    };
    return statusMap[status] || 'info';
}

function getActivityColor(type) {
    const colorMap = {
        'user': '#667eea',
        'post': '#f5576c',
        'campaign': '#4facfe',
        'donation': '#43e97b',
        'comment': '#f59e0b',
        'volunteer': '#10b981',
        'event': '#6366f1',
        'notification': '#6b7280'
    };
    return colorMap[type] || '#6b7280';
}

function getActivityIcon(type) {
    const icons = {
        'user': '👤',
        'post': '📝',
        'campaign': '🎯',
        'donation': '💰'
    };
    return icons[type] || '📌';
}

// Action functions
function viewUser(id) {
    alert(`Lihat detail pengguna ID: ${id}`);
}

function viewPost(id) {
    alert(`Lihat detail postingan ID: ${id}`);
}

function deletePost(id) {
    if (confirm('Apakah Anda yakin ingin menghapus postingan ini?')) {
        fetch(`${ADMIN_API_BASE}/posts/${id}`, {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    loadPosts();
                } else {
                    alert('Gagal menghapus postingan');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Terjadi kesalahan');
            });
    }
}

function viewCampaign(id) {
    alert(`Lihat detail kampanye ID: ${id}`);
}

function viewDonation(id) {
    alert(`Lihat detail donasi ID: ${id}`);
}

async function updateUserRole(id, currentRole) {
    const role = prompt("Role (user/admin):", currentRole);
    if (!role) return;
    if (!['user', 'admin'].includes(role)) {
        alert('Role tidak valid');
        return;
    }
    if (!confirm(`Yakin ubah role user #${id} menjadi ${role}?`)) return;

    try {
        const res = await fetch(`${ADMIN_API_BASE}/users/${id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role })
        });
        const data = await res.json();
        if (data.status === 'success') loadUsers();
        else alert(data.message || 'Gagal mengubah role');
    } catch (e) {
        console.error(e);
        alert('Terjadi kesalahan');
    }
}

function deleteUser(id) {
    if (confirm('Apakah Anda yakin ingin menghapus pengguna ini? Tindakan ini juga menghapus data terkait (posts/comments/volunteers).')) {
        fetch(`${ADMIN_API_BASE}/users/${id}`, { method: 'DELETE' })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') loadUsers();
                else alert(data.message || 'Gagal menghapus pengguna');
            })
            .catch(err => {
                console.error(err);
                alert('Terjadi kesalahan');
            });
    }
}

async function updateCampaignStatus(id, currentStatus) {
    const status = prompt("Status kampanye (active/completed/cancelled):", currentStatus);
    if (!status) return;
    if (!['active', 'completed', 'cancelled'].includes(status)) {
        alert('Status tidak valid');
        return;
    }
    try {
        const res = await fetch(`${ADMIN_API_BASE}/campaigns/${id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ campaign_status: status })
        });
        const data = await res.json();
        if (data.status === 'success') loadCampaigns();
        else alert(data.message || 'Gagal update status kampanye');
    } catch (e) {
        console.error(e);
        alert('Terjadi kesalahan');
    }
}

async function updateDonationStatus(id, currentStatus) {
    const status = prompt("Status donasi (pending/completed/failed/refunded):", currentStatus);
    if (!status) return;
    if (!['pending', 'completed', 'failed', 'refunded'].includes(status)) {
        alert('Status tidak valid');
        return;
    }
    try {
        const res = await fetch(`${ADMIN_API_BASE}/donations/${id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ donation_status: status })
        });
        const data = await res.json();
        if (data.status === 'success') loadDonations();
        else alert(data.message || 'Gagal update status donasi');
    } catch (e) {
        console.error(e);
        alert('Terjadi kesalahan');
    }
}

function deleteComment(id) {
    if (confirm('Apakah Anda yakin ingin menghapus komentar ini?')) {
        fetch(`${ADMIN_API_BASE}/comments/${id}`, { method: 'DELETE' })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') loadComments();
                else alert(data.message || 'Gagal menghapus komentar');
            })
            .catch(err => {
                console.error(err);
                alert('Terjadi kesalahan');
            });
    }
}

async function updateVolunteer(id, currentStatus, currentHours) {
    const status = prompt("Update status relawan (applied/accepted/rejected/completed):", currentStatus);
    if (!status) return;
    const hoursStr = prompt("Update jam kontribusi (angka):", String(currentHours ?? 0));
    if (hoursStr === null) return;
    const hours = Number(hoursStr);
    if (Number.isNaN(hours) || hours < 0) {
        alert('Jam kontribusi tidak valid');
        return;
    }

    try {
        const res = await fetch(`${ADMIN_API_BASE}/volunteers/${id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ volunteer_status: status, hours_contributed: hours })
        });
        const data = await res.json();
        if (data.status === 'success') loadVolunteers();
        else alert(data.message || 'Gagal update relawan');
    } catch (e) {
        console.error(e);
        alert('Terjadi kesalahan');
    }
}

function deleteNotification(id) {
    if (confirm('Apakah Anda yakin ingin menghapus notifikasi ini?')) {
        fetch(`${ADMIN_API_BASE}/notifications/${id}`, { method: 'DELETE' })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') loadNotifications();
                else alert(data.message || 'Gagal menghapus notifikasi');
            })
            .catch(err => {
                console.error(err);
                alert('Terjadi kesalahan');
            });
    }
}

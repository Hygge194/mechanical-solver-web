/**
 * user-dropdown.js – Shared script cho user dropdown & đăng xuất
 * Yêu cầu HTML có các id: userRowBtn, userDropdown, userAv, userName,
 *   userRole, dropName, dropEmail, btnLogout
 *
 * Cần load SAU storage.js trong HTML.
 */
(function () {
    'use strict';

    /* ── 1. Điền thông tin người dùng ─────────────────────────── */
    function fillUserInfo() {
        try {
            let user = null;
            const stored = localStorage.getItem('user');
            if (stored && stored !== 'undefined') {
                user = JSON.parse(stored);
            }
            const displayName = (user && (user.full_name || user.username)) || 'Người dùng';
            const email       = (user && user.email) || '—';
            const role        = (user && user.role)  || 'CS';

            const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };

            set('userName', displayName);
            set('userRole', role);
            set('dropName',  displayName);
            set('dropEmail', email);

            // Avatar initials
            const parts = displayName.trim().split(/\s+/);
            const initials = parts.length >= 2
                ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
                : parts[0].substring(0, 2).toUpperCase();
            set('userAv', initials);

        } catch (e) {
            console.error('[UserDropdown] Lỗi đọc user info:', e);
        }
    }

    /* ── 2. Gắn sự kiện dropdown ──────────────────────────────── */
    function initDropdown() {
        const row      = document.getElementById('userRowBtn');
        const dropdown = document.getElementById('userDropdown');
        const btnLogout = document.getElementById('btnLogout');

        if (!row || !dropdown) return;

        // Toggle khi click user-row
        row.addEventListener('click', function (e) {
            e.stopPropagation();
            dropdown.classList.toggle('open');
        });

        // Đóng khi click ra ngoài
        document.addEventListener('click', function () {
            dropdown.classList.remove('open');
        });

        // Ngăn dropdown tự đóng khi click bên trong
        dropdown.addEventListener('click', function (e) {
            e.stopPropagation();
        });

        /* ── Đăng xuất ── */
        if (btnLogout) {
            btnLogout.addEventListener('click', function () {
                if (!confirm('Bạn có chắc muốn đăng xuất?')) return;
                localStorage.removeItem('user');
                localStorage.removeItem('auth_token');
                // Tính đường dẫn login – hỗ trợ cả chạy từ thư mục root và subfolder
                const isInSubfolder = window.location.pathname.includes('/m1/')
                    || window.location.pathname.includes('/m2/')
                    || window.location.pathname.includes('/m3/')
                    || window.location.pathname.includes('/m4/');
                window.location.href = isInSubfolder ? '../login.html' : 'login.html';
            });
        }
    }

    /* ── 3. Chạy sau DOM ready ────────────────────────────────── */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            fillUserInfo();
            initDropdown();
        });
    } else {
        fillUserInfo();
        initDropdown();
    }
})();

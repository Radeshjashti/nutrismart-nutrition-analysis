/**
 * NutriSmart - Main Client-Side Script
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile Sidebar Toggle
    const sidebar = document.getElementById('appSidebar');
    const openBtn = document.getElementById('sidebarOpenBtn');
    const closeBtn = document.getElementById('sidebarCloseBtn');

    if (openBtn && sidebar) {
        openBtn.addEventListener('click', function() {
            sidebar.classList.add('show');
        });
    }

    if (closeBtn && sidebar) {
        closeBtn.addEventListener('click', function() {
            sidebar.classList.remove('show');
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (sidebar && sidebar.classList.contains('show')) {
            if (!sidebar.contains(e.target) && openBtn && !openBtn.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        }
    });

    // Auto-dismiss alerts after 6 seconds
    const alerts = document.querySelectorAll('.modern-alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            try {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            } catch (err) {}
        }, 6000);
    });
});

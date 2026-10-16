// ContactHub Main JavaScript
document.addEventListener('DOMContentLoaded', function () {
    // 1. Mobile Sidebar Toggle
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggleBtn');
    const closeBtn = document.getElementById('sidebarCloseBtn');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });
    }

    if (closeBtn && sidebar) {
        closeBtn.addEventListener('click', function () {
            sidebar.classList.remove('show');
        });
    }

    // Close sidebar on click outside in mobile view
    document.addEventListener('click', function (event) {
        if (sidebar && sidebar.classList.contains('show')) {
            if (!sidebar.contains(event.target) && !toggleBtn.contains(event.target)) {
                sidebar.classList.remove('show');
            }
        }
    });

    // 2. Auto-dismiss flash alerts after 5 seconds
    const alerts = document.querySelectorAll('.flash-messages-container .alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // 3. Dynamic Favorite Toggle via Fetch API
    const favoriteForms = document.querySelectorAll('.favorite-toggle-form');
    favoriteForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const actionUrl = form.getAttribute('action');
            const token = form.querySelector('input[name="csrf_token"]').value;
            const button = form.querySelector('.btn-favorite-toggle');
            const icon = button.querySelector('i');

            fetch(actionUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': token
                },
                body: new URLSearchParams({ csrf_token: token })
            })
            .then(function (res) {
                if (!res.ok) throw new Error('Network error');
                return res.json();
            })
            .then(function (data) {
                if (data.success) {
                    if (data.is_favorite === 1) {
                        button.classList.add('is-favorite');
                        icon.classList.remove('bi-star');
                        icon.classList.add('bi-star-fill');
                        button.setAttribute('title', 'Remove from Favorites');
                    } else {
                        button.classList.remove('is-favorite');
                        icon.classList.remove('bi-star-fill');
                        icon.classList.add('bi-star');
                        button.setAttribute('title', 'Mark as Favorite');
                    }
                }
            })
            .catch(function () {
                // Fallback to normal form submission if AJAX fails
                form.submit();
            });
        });
    });

    // 4. Initialize Bootstrap tooltips if any
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

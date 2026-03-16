// static/js/dashboard.js - Admin dashboard functionality

class DashboardApp {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadStats();
    }

    bindEvents() {
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', () => this.filterTable());
        }

        // Category filter
        const categoryFilter = document.getElementById('categoryFilter');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', () => this.filterTable());
        }

        // Sort button
        const sortBtn = document.getElementById('sortBtn');
        if (sortBtn) {
            sortBtn.addEventListener('click', () => this.sortTable());
        }
    }

    async loadStats() {
        try {
            // This would typically fetch from an API endpoint
            // For now, we'll calculate from the table data
            this.updateStatsFromTable();
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    updateStatsFromTable() {
        const table = document.getElementById('leadsTable');
        if (!table) return;

        const rows = table.querySelectorAll('tbody tr');
        let totalLeads = rows.length;
        let hotLeads = 0;
        let warmLeads = 0;
        let coldLeads = 0;

        rows.forEach(row => {
            const categoryCell = row.cells[5]; // Lead Category column
            if (categoryCell) {
                const category = categoryCell.textContent.trim().toLowerCase();
                if (category.includes('hot')) hotLeads++;
                else if (category.includes('warm')) warmLeads++;
                else if (category.includes('cold')) coldLeads++;
            }
        });

        // Update stat cards
        this.updateStatCard('totalLeads', totalLeads);
        this.updateStatCard('hotLeads', hotLeads);
        this.updateStatCard('warmLeads', warmLeads);
        this.updateStatCard('coldLeads', coldLeads);
        this.updateStatCard('messagesToday', 0); // Would need API for this
    }

    updateStatCard(cardId, value) {
        const card = document.querySelector(`.stat-card.${cardId}`);
        if (card) {
            const valueElement = card.querySelector('h3');
            if (valueElement) {
                valueElement.textContent = value.toLocaleString();
            }
        }
    }

    filterTable() {
        const searchInput = document.getElementById('searchInput');
        const categoryFilter = document.getElementById('categoryFilter');
        const table = document.getElementById('leadsTable');

        if (!table) return;

        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const categoryValue = categoryFilter ? categoryFilter.value : '';
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const phoneCell = row.cells[0]; // Phone/User ID column
            const categoryCell = row.cells[5]; // Category column

            const phoneText = phoneCell ? phoneCell.textContent.toLowerCase() : '';
            const categoryText = categoryCell ? categoryCell.textContent.trim() : '';

            const matchesSearch = !searchTerm || phoneText.includes(searchTerm);
            const matchesCategory = !categoryValue || categoryText === categoryValue;

            row.style.display = matchesSearch && matchesCategory ? '' : 'none';
        });

        // Update stats after filtering
        this.updateStatsFromTable();
    }

    sortTable() {
        const table = document.getElementById('leadsTable');
        if (!table) return;

        const tbody = table.querySelector('tbody');
        if (!tbody) return;

        const rows = Array.from(tbody.querySelectorAll('tr'));

        rows.sort((a, b) => {
            const dateA = new Date(a.cells[6].textContent); // Last Interaction column
            const dateB = new Date(b.cells[6].textContent);

            return dateB - dateA; // Descending order (newest first)
        });

        // Clear tbody and append sorted rows
        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));

        this.showNotification('Table sorted by last interaction (newest first)', 'success');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : 'success'} notification`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            padding: 12px 16px;
            border-radius: 6px;
            color: white;
            background-color: ${type === 'error' ? '#dc3545' : '#28a745'};
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-width: 300px;
            opacity: 0;
            transform: translateY(-20px);
            transition: all 0.3s ease;
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        }, 100);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-20px)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Utility function to format phone numbers
    formatPhoneNumber(phone) {
        if (!phone) return phone;
        // Remove whatsapp: prefix if present
        return phone.replace(/^whatsapp:\+?/, '+');
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DashboardApp();
});
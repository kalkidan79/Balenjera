/**
 * Balenjera - Main JavaScript File
 * Handles common functionality across all pages
 * Version: Final
 */

// ==================== DOM Ready ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌸 Balenjera Wellness Platform Loaded');
    
    // ==================== Mobile Menu Toggle ====================
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');
    
    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('show');
        });
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (navLinks && navLinks.classList.contains('show')) {
            if (!navLinks.contains(event.target) && !mobileMenuBtn.contains(event.target)) {
                navLinks.classList.remove('show');
            }
        }
    });
    
    // ==================== Smooth Scrolling ====================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            if (href.startsWith('#') && href !== '#') {
                e.preventDefault();
                const targetElement = document.querySelector(href);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 80,
                        behavior: 'smooth'
                    });
                    
                    // Close mobile menu if open
                    if (navLinks && navLinks.classList.contains('show')) {
                        navLinks.classList.remove('show');
                    }
                }
            }
        });
    });
    
    // ==================== Check Authentication Status ====================
    function checkAuthStatus() {
        const isLoggedIn = localStorage.getItem('balenjeraLoggedIn') === 'true';
        const userData = JSON.parse(localStorage.getItem('balenjeraUser') || '{}');
        return { isLoggedIn, userData };
    }
    
    // Update navigation based on auth status
    function updateNavigation() {
        const { isLoggedIn, userData } = checkAuthStatus();
        const loginBtn = document.getElementById('loginNavBtn');
        const dashboardBtn = document.getElementById('dashboardNavBtn');
        
        console.log('Navigation update - isLoggedIn:', isLoggedIn);
        
        if (isLoggedIn && loginBtn && dashboardBtn) {
            loginBtn.style.display = 'none';
            dashboardBtn.style.display = 'flex';
            
            // Update dashboard button text with user name
            const userName = userData.name || 'Profile';
            dashboardBtn.innerHTML = `<i class="fas fa-user-circle"></i> ${userName}`;
            dashboardBtn.href = userData.role === 'counselor' ? 'counselor.html' : 'dashboard.html';
        } else if (loginBtn && dashboardBtn) {
            loginBtn.style.display = 'flex';
            dashboardBtn.style.display = 'none';
            if (loginBtn.tagName === 'A') {
                loginBtn.href = 'login.html';
            }
        }
    }
    
    // ==================== Logout Function ====================
    window.logout = function() {
        if (confirm('Are you sure you want to logout?')) {
            localStorage.removeItem('balenjeraLoggedIn');
            localStorage.removeItem('balenjeraUser');
            localStorage.removeItem('balenjeraMemberSince');
            window.location.href = 'index.html';
        }
    };
    
    // ==================== Show Toast Message ====================
    window.showToast = function(message, type = 'info') {
        // Remove existing toast
        const existingToast = document.querySelector('.custom-toast');
        if (existingToast) existingToast.remove();
        
        const toast = document.createElement('div');
        toast.className = 'custom-toast';
        
        let bgColor = '#3498db';
        let icon = 'ℹ️';
        
        if (type === 'success') {
            bgColor = '#2ecc71';
            icon = '✅';
        } else if (type === 'error') {
            bgColor = '#e74c3c';
            icon = '❌';
        } else if (type === 'warning') {
            bgColor = '#f39c12';
            icon = '⚠️';
        }
        
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: ${bgColor};
            color: white;
            padding: 12px 20px;
            border-radius: 10px;
            z-index: 10000;
            font-size: 0.9rem;
            animation: slideInRight 0.3s ease;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 10px;
        `;
        toast.innerHTML = `${icon} ${message}`;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    };
    
    // ==================== API Helper Functions ====================
    const API_BASE_URL = 'http://localhost:5000/api';
    
    window.apiRequest = async function(endpoint, method = 'GET', data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Request failed');
            }
            
            return result;
        } catch (error) {
            console.error('API Error:', error);
            showToast(error.message, 'error');
            throw error;
        }
    };
    
    // ==================== Load Sample Data ====================
    window.loadSampleData = async function() {
        try {
            const response = await fetch(`${API_BASE_URL}/sample-data`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Failed to load sample data:', error);
            return null;
        }
    };
    
    // ==================== Save Chat to History ====================
    window.saveChatToHistory = function(userMessage, aiResponse, severity = 'normal') {
        let chatHistory = JSON.parse(localStorage.getItem('balenjeraChatHistory') || '[]');
        chatHistory.push({
            id: Date.now(),
            timestamp: new Date().toISOString(),
            user_message: userMessage,
            ai_response: aiResponse,
            preview: userMessage.substring(0, 80),
            severity: severity
        });
        // Keep only last 50 chats
        while (chatHistory.length > 50) chatHistory.shift();
        localStorage.setItem('balenjeraChatHistory', JSON.stringify(chatHistory));
    };
    
    // ==================== Load Chat History ====================
    window.loadChatHistory = function() {
        return JSON.parse(localStorage.getItem('balenjeraChatHistory') || '[]');
    };
    
    // ==================== Animation Styles ====================
    function addAnimationStyles() {
        if (document.getElementById('balenjera-animation-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'balenjera-animation-styles';
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            .fa-spin {
                animation: spin 1s linear infinite;
            }
        `;
        document.head.appendChild(style);
    }
    addAnimationStyles();
    
    // ==================== Initialize Page ====================
    updateNavigation();
    
    // Add scroll effect to navbar
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
                navbar.style.background = 'rgba(255, 255, 255, 0.98)';
            } else {
                navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.05)';
                navbar.style.background = 'rgba(255, 255, 255, 0.98)';
            }
        });
    }
    
    // ==================== Helper: Escape HTML ====================
    window.escapeHtml = function(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    };
    
    // ==================== Helper: Format Date ====================
    window.formatDate = function(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 60) {
            return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
        } else if (diffHours < 24) {
            return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
        } else if (diffDays < 7) {
            return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
        } else {
            return date.toLocaleDateString();
        }
    };
    
    // ==================== Helper: Get Initials ====================
    window.getInitials = function(name) {
        if (!name) return 'U';
        return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
    };
    
    console.log('✅ Balenjera main.js loaded successfully');
});
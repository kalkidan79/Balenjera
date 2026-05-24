/**
 * Balenjera - Authentication JavaScript
 * Fixed version with better error handling
 */

const API_BASE_URL = 'http://localhost:5000/api';

// ==================== DOM Ready ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔐 Balenjera Auth System Loaded');
    console.log('📡 API URL:', API_BASE_URL);
    
    // Check if already logged in
    const isLoggedIn = localStorage.getItem('balenjeraLoggedIn') === 'true';
    if (isLoggedIn && window.location.pathname.includes('login.html')) {
        const userData = JSON.parse(localStorage.getItem('balenjeraUser') || '{}');
        if (userData.role === 'counselor') {
            window.location.href = 'counselor.html';
        } else {
            window.location.href = 'dashboard.html';
        }
        return;
    }
    
    // Initialize forms
    initLoginForm();
    initSignupForm();
    
    // Test backend connection
    testBackendConnection();
});

// ==================== Test Backend Connection ====================
async function testBackendConnection() {
    try {
        console.log('Testing backend connection...');
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend connected!', data);
            showToast('Connected to server', 'success');
        } else {
            console.error('❌ Backend returned error:', response.status);
            showToast('Server connection issue. Please make sure backend is running on port 5000', 'error');
        }
    } catch (error) {
        console.error('❌ Cannot connect to backend:', error);
        showToast('Cannot connect to server. Please run: python app.py in the backend folder', 'error');
    }
}

// ==================== Login Form Handler ====================
function initLoginForm() {
    const loginForm = document.getElementById('loginFormElement');
    if (!loginForm) return;
    
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Clear previous errors
        clearErrors('login');
        
        // Get values
        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;
        
        // Validate
        let isValid = true;
        
        if (!email) {
            showError('loginEmailError', 'Email is required');
            isValid = false;
        } else if (!isValidEmail(email)) {
            showError('loginEmailError', 'Please enter a valid email address');
            isValid = false;
        }
        
        if (!password) {
            showError('loginPasswordError', 'Password is required');
            isValid = false;
        }
        
        if (!isValid) return;
        
        // Show loading state
        const loginBtn = document.getElementById('loginBtn');
        const originalText = loginBtn.innerHTML;
        loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing In...';
        loginBtn.disabled = true;
        
        try {
            console.log('Attempting login for:', email);
            
            const response = await fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            console.log('Login response status:', response.status);
            const data = await response.json();
            console.log('Login response data:', data);
            
            if (!response.ok) {
                throw new Error(data.error || 'Login failed');
            }
            
            // Save to localStorage
            localStorage.setItem('balenjeraLoggedIn', 'true');
            localStorage.setItem('balenjeraUser', JSON.stringify(data.user));
            
            showToast(`Welcome back, ${data.user.name}!`, 'success');
            
            // Redirect based on role
            setTimeout(() => {
                if (data.user.role === 'counselor') {
                    window.location.href = 'counselor.html';
                } else {
                    window.location.href = 'dashboard.html';
                }
            }, 1000);
            
        } catch (error) {
            console.error('Login error:', error);
            showToast(error.message || 'Login failed. Please check your credentials.', 'error');
            
            loginBtn.innerHTML = originalText;
            loginBtn.disabled = false;
        }
    });
}

// ==================== Signup Form Handler (FIXED) ====================
function initSignupForm() {
    const signupForm = document.getElementById('signupFormElement');
    if (!signupForm) return;
    
    signupForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        console.log('Signup form submitted');
        
        // Clear previous errors
        clearErrors('signup');
        
        // Get values
        const name = document.getElementById('signupName').value.trim();
        const email = document.getElementById('signupEmail').value.trim();
        const password = document.getElementById('signupPassword').value;
        const confirmPassword = document.getElementById('signupConfirmPassword').value;
        const role = document.querySelector('input[name="role"]:checked')?.value || 'student';
        
        console.log('Signup data:', { name, email, role });
        
        // Validate
        let isValid = true;
        
        if (!name) {
            showError('signupNameError', 'Full name is required');
            isValid = false;
        } else if (name.length < 2) {
            showError('signupNameError', 'Name must be at least 2 characters');
            isValid = false;
        }
        
        if (!email) {
            showError('signupEmailError', 'Email is required');
            isValid = false;
        } else if (!isValidEmail(email)) {
            showError('signupEmailError', 'Please enter a valid email address');
            isValid = false;
        }
        
        if (!password) {
            showError('signupPasswordError', 'Password is required');
            isValid = false;
        } else if (password.length < 6) {
            showError('signupPasswordError', 'Password must be at least 6 characters');
            isValid = false;
        }
        
        if (password !== confirmPassword) {
            showError('signupConfirmError', 'Passwords do not match');
            isValid = false;
        }
        
        if (!isValid) return;
        
        // Show loading state
        const signupBtn = document.getElementById('signupBtn');
        const originalText = signupBtn.innerHTML;
        signupBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Account...';
        signupBtn.disabled = true;
        
        try {
            console.log('Sending registration request to:', `${API_BASE_URL}/register`);
            
            const response = await fetch(`${API_BASE_URL}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password, role })
            });
            
            console.log('Registration response status:', response.status);
            const data = await response.json();
            console.log('Registration response data:', data);
            
            if (!response.ok) {
                throw new Error(data.error || 'Registration failed');
            }
            
            showToast(`Welcome to Balenjera, ${name}!`, 'success');
            
            // Auto-login after registration
            console.log('Auto-login attempt...');
            const loginResponse = await fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            const loginData = await loginResponse.json();
            console.log('Auto-login response:', loginData);
            
            if (loginResponse.ok) {
                localStorage.setItem('balenjeraLoggedIn', 'true');
                localStorage.setItem('balenjeraUser', JSON.stringify(loginData.user));
            }
            
            // Redirect after 1.5 seconds
            setTimeout(() => {
                if (role === 'counselor') {
                    window.location.href = 'counselor.html';
                } else {
                    window.location.href = 'dashboard.html';
                }
            }, 1500);
            
        } catch (error) {
            console.error('Signup error details:', error);
            
            let errorMessage = error.message;
            if (error.message === 'Failed to fetch') {
                errorMessage = 'Cannot connect to server. Please make sure the backend is running (python app.py)';
            }
            
            showToast(errorMessage, 'error');
            
            signupBtn.innerHTML = originalText;
            signupBtn.disabled = false;
        }
    });
}

// ==================== Helper Functions ====================

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.add('show');
        
        // Find the input field and highlight it
        const input = document.getElementById(elementId.replace('Error', ''));
        if (input) {
            input.classList.add('error');
        }
    }
}

function clearErrors(formType) {
    const errorIds = formType === 'login' 
        ? ['loginEmailError', 'loginPasswordError']
        : ['signupNameError', 'signupEmailError', 'signupPasswordError', 'signupConfirmError'];
    
    errorIds.forEach(id => {
        const errorElement = document.getElementById(id);
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.classList.remove('show');
        }
    });
    
    // Remove error class from all inputs
    document.querySelectorAll('.form-input').forEach(input => {
        input.classList.remove('error');
    });
}

function showToast(message, type = 'info') {
    // Remove existing toast
    const existingToast = document.querySelector('.custom-toast');
    if (existingToast) existingToast.remove();
    
    const toast = document.createElement('div');
    toast.className = 'custom-toast';
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${type === 'success' ? '#2ecc71' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        z-index: 10000;
        font-size: 0.9rem;
        animation: slideInRight 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    `;
    toast.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i> ${message}`;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ==================== Check Auth Status ====================
window.checkAuth = function() {
    const isLoggedIn = localStorage.getItem('balenjeraLoggedIn') === 'true';
    const userData = JSON.parse(localStorage.getItem('balenjeraUser') || '{}');
    return { isLoggedIn, userData };
};

// ==================== Logout Function ====================
window.logout = function() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('balenjeraLoggedIn');
        localStorage.removeItem('balenjeraUser');
        window.location.href = 'index.html';
    }
};

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
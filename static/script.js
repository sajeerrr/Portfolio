/**
 * PORTFOLIO SCRIPT — All frontend interactions
 * Handles animations, API calls, event listeners, and UI updates
 */

// ============ GLOBAL STATE ============
const state = {
    portfolioData: null,
    lastUpdated: null,
    projects: [],
    animationsInitialized: false,
    mobileMenuOpen: false,
};

// ============ INITIALIZATION ============
document.addEventListener('DOMContentLoaded', () => {
    initializeCursorGlow();
    initializeParticleCanvas();
    initializeNeuralCanvas();
    initializeTypewriter();
    initializeNavbar();
    initializeScrollAnimations();
    initializeProgressBars();
    initializeProjectCards();
    initializeContactForm();
    initializeBackToTop();
    initializeMobileMenu();
    setupEventListeners();
});

// ============ CURSOR GLOW ============
function initializeCursorGlow() {
    const cursorGlow = document.getElementById('cursor-glow');
    if (!cursorGlow) return;

    document.addEventListener('mousemove', (e) => {
        cursorGlow.style.left = e.clientX + 'px';
        cursorGlow.style.top = e.clientY + 'px';
    });

    document.addEventListener('mouseenter', () => {
        cursorGlow.style.display = 'block';
    });

    document.addEventListener('mouseleave', () => {
        cursorGlow.style.display = 'none';
    });
}

// ============ PARTICLE BACKGROUND CANVAS ============
function initializeParticleCanvas() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let width = 0;
    let height = 0;

    const particles = [];
    const particleCount = Math.min(90, Math.max(42, Math.floor(window.innerWidth / 18)));

    function resizeCanvas() {
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        width = window.innerWidth;
        height = canvas.parentElement.offsetHeight;
        canvas.width = Math.floor(width * dpr);
        canvas.height = Math.floor(height * dpr);
        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    class Particle {
        constructor() {
            this.reset();
        }

        reset() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.size = Math.random() * 1.8 + 0.6;
            this.speedX = (Math.random() - 0.5) * 0.28;
            this.speedY = (Math.random() - 0.5) * 0.28;
            this.opacity = Math.random() * 0.45 + 0.16;
            const palette = ['230, 57, 70', '255, 255, 255', '0, 212, 255'];
            this.color = palette[Math.floor(Math.random() * palette.length)];
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            if (this.x > width) this.x = 0;
            if (this.x < 0) this.x = width;
            if (this.y > height) this.y = 0;
            if (this.y < 0) this.y = height;
        }

        draw() {
            ctx.shadowBlur = 18;
            ctx.shadowColor = `rgba(${this.color}, ${this.opacity * 0.45})`;
            ctx.fillStyle = `rgba(${this.color}, ${this.opacity})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    resizeCanvas();
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }

    function drawConnections() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                if (distance < 115) {
                    ctx.strokeStyle = `rgba(230, 57, 70, ${(1 - distance / 115) * 0.11})`;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);

        drawConnections();
        particles.forEach((particle) => {
            if (!prefersReducedMotion) particle.update();
            particle.draw();
        });

        ctx.shadowBlur = 0;
        requestAnimationFrame(animate);
    }

    animate();

    window.addEventListener('resize', () => {
        resizeCanvas();
        particles.forEach((particle) => particle.reset());
    });
}

// ============ NEURAL CANVAS (Right side of hero) ============
function initializeNeuralCanvas() {
    const canvas = document.getElementById('neural-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let width = 0;
    let height = 0;

    const nodes = [];
    const nodeCount = 24;

    function resizeCanvas() {
        const rect = canvas.getBoundingClientRect();
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        width = rect.width;
        height = rect.height;
        canvas.width = Math.floor(width * dpr);
        canvas.height = Math.floor(height * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    class Node {
        constructor() {
            this.reset();
        }

        reset() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.size = Math.random() * 3 + 3;
            this.speedX = (Math.random() - 0.5) * 0.34;
            this.speedY = (Math.random() - 0.5) * 0.34;
            this.pulse = 0;
            this.hue = Math.random() > 0.82 ? 192 : Math.random() * 24 + 348;
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            if (this.x - this.size < 0 || this.x + this.size > width)
                this.speedX *= -1;
            if (this.y - this.size < 0 || this.y + this.size > height)
                this.speedY *= -1;

            this.pulse = Math.sin(Date.now() / 800) * 0.5 + 1;
        }

        draw() {
            const color = `hsla(${this.hue}, 80%, 55%, ${0.8 * this.pulse})`;
            const glowColor = `hsla(${this.hue}, 80%, 55%, ${0.4 * this.pulse})`;

            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();

            // Outer glow ring
            ctx.strokeStyle = glowColor;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size + 8, 0, Math.PI * 2);
            ctx.stroke();

            // Inner glow
            ctx.shadowBlur = 20;
            ctx.shadowColor = glowColor;
        }
    }

    resizeCanvas();
    for (let i = 0; i < nodeCount; i++) {
        nodes.push(new Node());
    }

    function drawConnections() {
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const dx = nodes[i].x - nodes[j].x;
                const dy = nodes[i].y - nodes[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 180) {
                    const opacity = (1 - distance / 180) * 0.3;
                    ctx.strokeStyle = `rgba(230, 57, 70, ${opacity})`;
                    ctx.lineWidth = 1.5;
                    ctx.beginPath();
                    ctx.moveTo(nodes[i].x, nodes[i].y);
                    ctx.lineTo(nodes[j].x, nodes[j].y);
                    ctx.stroke();
                }
            }
        }
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);

        drawConnections();

        nodes.forEach((node) => {
            if (!prefersReducedMotion) node.update();
            node.draw();
        });

        ctx.shadowBlur = 0;
        requestAnimationFrame(animate);
    }

    animate();

    window.addEventListener('resize', () => {
        resizeCanvas();
        nodes.forEach((node) => node.reset());
    });
}

// ============ TYPEWRITER EFFECT ============
function initializeTypewriter() {
    const typewriterElement = document.getElementById('typewriter');
    if (!typewriterElement) return;

    const texts = ['Python Dev', 'AI Enthusiast', 'Backend Engineer'];
    let currentIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let speed = 100;

    function typeEffect() {
        const currentText = texts[currentIndex];

        if (isDeleting) {
            typewriterElement.textContent = currentText.substring(0, charIndex - 1);
            charIndex--;
        } else {
            typewriterElement.textContent = currentText.substring(0, charIndex + 1);
            charIndex++;
        }

        // When typing is complete, pause before deleting
        if (!isDeleting && charIndex === currentText.length) {
            speed = 1500; // Pause before deleting
            isDeleting = true;
        } else if (isDeleting && charIndex === 0) {
            // Move to next text
            currentIndex = (currentIndex + 1) % texts.length;
            isDeleting = false;
            speed = 100;
        } else {
            speed = isDeleting ? 50 : 100;
        }

        setTimeout(typeEffect, speed);
    }

    typeEffect();
}

// ============ NAVBAR SCROLL DETECTION ============
function initializeNavbar() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Smooth scroll and active link
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('section');

    window.addEventListener('scroll', () => {
        let current = '';
        sections.forEach((section) => {
            const sectionTop = section.offsetTop;
            if (pageYOffset >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach((link) => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });

    // Close mobile menu when link clicked
    navLinks.forEach((link) => {
        link.addEventListener('click', () => {
            closeMobileMenu();
        });
    });
}

// ============ MOBILE MENU ============
function initializeMobileMenu() {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');

    if (!navToggle || !navMenu) return;

    navToggle.addEventListener('click', () => {
        state.mobileMenuOpen = !state.mobileMenuOpen;
        if (state.mobileMenuOpen) {
            navMenu.classList.add('active');
        } else {
            navMenu.classList.remove('active');
        }
    });
}

function closeMobileMenu() {
    const navMenu = document.getElementById('nav-menu');
    state.mobileMenuOpen = false;
    if (navMenu) {
        navMenu.classList.remove('active');
    }
}

// ============ SCROLL ANIMATIONS ============
function initializeScrollAnimations() {
    // Intersection Observer for fade-in-on-scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
            }
        });
    }, {
        threshold: 0.1,
    });

    document.querySelectorAll('.animate-on-scroll').forEach((el) => {
        observer.observe(el);
    });
}

// ============ PROGRESS BARS ============
function initializeProgressBars() {
    const progressBars = document.querySelectorAll('.progress-fill');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                const width = entry.target.dataset.width;
                entry.target.style.setProperty('--target-width', `${width}%`);
                entry.target.dataset.animated = 'true';
            }
        });
    }, {
        threshold: 0.5,
    });

    progressBars.forEach((bar) => {
        observer.observe(bar);
    });
}

// ============ PROJECT CARDS ============
async function initializeProjectCards() {
    try {
        const response = await fetch('/api/github');
        const data = await response.json();

        state.portfolioData = data;
        state.lastUpdated = new Date(data.last_updated);

        const repos = normalizeProjectList(data.repos || []);

        state.projects = repos;
        renderProjectCards(repos);
        updateLastSyncedTime();
    } catch (error) {
        console.error('Failed to load projects:', error);
        showToast('Failed to load projects', 'error');
    }
}

function renderProjectCards(repos) {
    const projectsGrid = document.getElementById('projects-grid');
    if (!projectsGrid) return;

    projectsGrid.innerHTML = '';

    repos.forEach((repo) => {
        const card = createProjectCard(repo);
        projectsGrid.appendChild(card);
    });

    // Add animation to cards
    document.querySelectorAll('.project-card').forEach((card) => {
        card.style.animation = 'fadeInUp 0.6s ease-out forwards';
    });
}

function normalizeProjectList(repos) {
    const normalized = repos.slice(0, 6);

    while (normalized.length < 6) {
        normalized.push({
            name: 'Coming Soon',
            description: 'Project in development...',
            html_url: '#',
            homepage: null,
            language: null,
            stargazers_count: 0,
            forks_count: 0,
            topics: [],
            updated_at: new Date().toISOString(),
        });
    }

    return normalized;
}

function createProjectCard(repo) {
    const card = document.createElement('div');
    card.className = 'project-card';

    const topics = Array.isArray(repo.topics) ? repo.topics : [];
    const repoName = repo.name || 'Untitled Project';
    const formattedName = repoName.replace(/[-_]/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
    const lastUpdated = repo.updated_at ? getRelativeTime(new Date(repo.updated_at)) : 'Recently';
    const language = repo.language ? String(repo.language) : '';
    const languageClass = language ? language.toLowerCase().replace(/[^a-z0-9-]/g, '-') : '';

    card.innerHTML = `
        <div class="project-header">
            <h3 class="project-name">${escapeHtml(formattedName)}</h3>
            ${language ? `<span class="project-language language-${languageClass}">${escapeHtml(language)}</span>` : ''}
        </div>
        <p class="project-description">${escapeHtml(repo.description || 'No description provided')}</p>
        <div class="project-tags">
            ${topics.map((topic) => `<span class="project-tag">${escapeHtml(topic)}</span>`).join('')}
        </div>
        <div class="project-stats">
            <span><i class="fas fa-star"></i> ${repo.stargazers_count}</span>
            <span><i class="fas fa-code-branch"></i> ${repo.forks_count}</span>
        </div>
        <p class="project-updated"><i class="fas fa-clock"></i> Updated ${lastUpdated}</p>
        <div class="project-buttons">
            ${repo.html_url !== '#' ? `<a href="${escapeAttribute(repo.html_url)}" target="_blank" rel="noopener noreferrer"><i class="fas fa-code"></i> View Code</a>` : '<a class="is-disabled" aria-disabled="true">View Code</a>'}
            ${repo.homepage ? `<a href="${escapeAttribute(repo.homepage)}" target="_blank" rel="noopener noreferrer"><i class="fas fa-external-link-alt"></i> Live Demo</a>` : ''}
        </div>
    `;

    return card;
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function escapeAttribute(value) {
    const url = String(value || '#').trim();
    if (!/^https?:\/\//i.test(url) && url !== '#') return '#';
    return escapeHtml(url);
}

function getLanguageColor(language) {
    const colors = {
        python: '#3776ab',
        javascript: '#ffd700',
        php: '#a855f7',
        html: '#e34c26',
        java: '#007396',
        c: '#a9b8fe',
    };
    return colors[language?.toLowerCase()] || '#b0b0b0';
}

function getRelativeTime(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    if (diffHours > 0) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffMins > 0) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    return 'just now';
}

function updateLastSyncedTime() {
    const lastSyncedEl = document.getElementById('last-synced');
    if (lastSyncedEl && state.lastUpdated) {
        lastSyncedEl.textContent = `Last synced: ${getRelativeTime(state.lastUpdated)}`;
    }
}

// ============ REFRESH PROJECTS ============
function setupRefreshButton() {
    const refreshBtn = document.getElementById('btn-refresh-projects');
    if (!refreshBtn) return;

    refreshBtn.addEventListener('click', async () => {
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';

        try {
            const response = await fetch('/api/refresh', { method: 'POST' });
            const data = await response.json();

            if (data.status === 'refreshed') {
                state.lastUpdated = new Date(data.data.last_updated);
                state.projects = normalizeProjectList(data.data.repos || []);
                renderProjectCards(state.projects);
                updateLastSyncedTime();
                showToast('Projects refreshed!', 'success');
            }
        } catch (error) {
            console.error('Refresh failed:', error);
            showToast('Failed to refresh projects', 'error');
        } finally {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh Projects';
        }
    });
}

// ============ CONTACT FORM ============
function initializeContactForm() {
    const contactForm = document.getElementById('contact-form');
    if (!contactForm) return;

    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('form-name').value;
        const email = document.getElementById('form-email').value;
        const message = document.getElementById('form-message').value;

        if (!name || !email || !message) {
            showToast('Please fill in all fields', 'error');
            return;
        }

        try {
            const response = await fetch('/api/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, message }),
            });

            const data = await response.json();

            if (data.status === 'sent') {
                showToast('Message sent! Thank you!', 'success');
                contactForm.reset();
            }
        } catch (error) {
            console.error('Contact form error:', error);
            showToast('Failed to send message', 'error');
        }
    });
}

// ============ BACK TO TOP ============
function initializeBackToTop() {
    const backToTopBtn = document.getElementById('back-to-top');
    if (!backToTopBtn) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTopBtn.classList.add('show');
        } else {
            backToTopBtn.classList.remove('show');
        }
    });

    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// ============ TOAST NOTIFICATION ============
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');

    if (!toast || !toastMessage) return;

    toastMessage.textContent = message;

    if (type === 'error') {
        toast.style.background = '#dc2626';
    } else {
        toast.style.background = '#e63946';
    }

    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ============ EVENT LISTENERS SETUP ============
function setupEventListeners() {
    // Hire Me button scroll to contact
    const hireMeBtn = document.getElementById('nav-cta');
    if (hireMeBtn) {
        hireMeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const contactSection = document.getElementById('contact');
            if (contactSection) {
                contactSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }

    // View My Work button
    const viewWorkBtn = document.getElementById('btn-view-work');
    if (viewWorkBtn) {
        viewWorkBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const projectsSection = document.getElementById('projects');
            if (projectsSection) {
                projectsSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }

    // Resume download button
    const resumeBtn = document.getElementById('btn-resume');
    if (resumeBtn) {
        resumeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            showToast('Resume link would go here', 'success');
        });
    }

    // Refresh projects button
    setupRefreshButton();

    // Secret admin access: Press 'a' + 'd' + 'm' + 'i' + 'n' in sequence
    setupSecretAdminAccess();
}

// ============ SECRET ADMIN ACCESS ============
function setupSecretAdminAccess() {
    const secretCode = ['a', 'd', 'm', 'i', 'n'];
    let currentIndex = 0;

    document.addEventListener('keydown', (e) => {
        if (e.key === secretCode[currentIndex]) {
            currentIndex++;
            if (currentIndex === secretCode.length) {
                window.location.href = '/admin';
                currentIndex = 0;
            }
        } else {
            currentIndex = 0;
        }
    });
}

// ============ UTILITY: Get initial portfolio data from template ============
// This allows the page to render initially without JS, with Jinja2 data
document.addEventListener('DOMContentLoaded', () => {
    // Update last-synced time if portfolio data is in the page
    const lastSyncedEl = document.getElementById('last-synced');
    if (lastSyncedEl && lastSyncedEl.textContent.includes('loading')) {
        // Time will be set when API data loads
    }
});

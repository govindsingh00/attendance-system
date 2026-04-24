/* ============================================
   E-Attendance System — Shared JavaScript
   Features: Navbar scroll, AOS init, utilities
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {
  initNavbarScroll();
  initAOS();
  initBootstrapComponents();
});

/* ============================================
   NAVBAR SCROLL EFFECT
   Transparent to solid white after 60px scroll
   ============================================ */
function initNavbarScroll() {
  const navbar = document.querySelector('.navbar-custom');
  if (!navbar) return;

  const scrollThreshold = 60;

  function updateNavbar() {
    if (window.scrollY > scrollThreshold) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }

  // Run once on load
  updateNavbar();

  // Listen for scroll
  window.addEventListener('scroll', updateNavbar, { passive: true });
}

/* ============================================
   AOS (Animate On Scroll) Initialization
   ============================================ */
function initAOS() {
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 700,
      easing: 'ease-out-cubic',
      once: true,
      offset: 60,
      disable: function () {
        // Disable on very small screens if needed
        return window.innerWidth < 360;
      }
    });
  }
}

/* ============================================
   BOOTSTRAP COMPONENTS INIT
   ============================================ */
function initBootstrapComponents() {
  // Initialize all tooltips
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  if (tooltipTriggerList.length && typeof bootstrap !== 'undefined') {
    [...tooltipTriggerList].forEach(el => new bootstrap.Tooltip(el));
  }

  // Initialize all popovers
  const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
  if (popoverTriggerList.length && typeof bootstrap !== 'undefined') {
    [...popoverTriggerList].forEach(el => new bootstrap.Popover(el));
  }
}

/* ============================================
   UTILITY FUNCTIONS
   ============================================ */

/**
 * Debounce function to limit how often a function can fire.
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Simple date formatter.
 */
function formatDate(date) {
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

/**
 * Highlight active nav link based on current page.
 */
function highlightActiveNav() {
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  const navLinks = document.querySelectorAll('.navbar-custom .nav-link');
  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href && href.includes(currentPage)) {
      link.classList.add('active');
    }
  });
}

// Run nav highlight on load
document.addEventListener('DOMContentLoaded', highlightActiveNav);

document.addEventListener('DOMContentLoaded', () => {
  const navLinks = document.querySelectorAll('.site-nav a');
  const currentPath = window.location.pathname.replace(/\/+/g, '/');

  navLinks.forEach((link) => {
    const href = link.getAttribute('href');
    if (currentPath.endsWith(href) || (href !== '/' && currentPath.includes(href))) {
      link.classList.add('active');
      link.setAttribute('aria-current', 'page');
    }
  });

  const revealElements = document.querySelectorAll('.panel, .hero-panel, .table-panel, .empty-state, .summary-card, .club-card');
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active');
        revealObserver.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.18,
  });

  revealElements.forEach((el) => {
    el.classList.add('reveal');
    revealObserver.observe(el);
  });

  const footerText = document.querySelector('.site-footer p');
  if (footerText) {
    const year = new Date().getFullYear();
    footerText.textContent = `© ${year} 轉社管理系統`;
  }
});

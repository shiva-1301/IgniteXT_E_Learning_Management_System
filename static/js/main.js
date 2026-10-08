// Shared UI behaviour: theme toggle, sidebar drawer, user menu, search, alerts
(function () {
    const root = document.documentElement;

    function storageGet(key) {
        try { return localStorage.getItem(key); } catch (e) { return null; }
    }
    function storageSet(key, value) {
        try { localStorage.setItem(key, value); } catch (e) { /* ignore */ }
    }

    // ----- Dark mode -----
    const toggleBtn = document.getElementById('toggle-btn');
    function applyTheme(dark) {
        root.setAttribute('data-theme', dark ? 'dark' : 'light');
        if (toggleBtn) {
            const icon = toggleBtn.querySelector('i');
            icon.className = dark ? 'fas fa-sun' : 'fas fa-moon';
            toggleBtn.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
        }
    }
    applyTheme(root.getAttribute('data-theme') === 'dark');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const dark = root.getAttribute('data-theme') !== 'dark';
            applyTheme(dark);
            storageSet('dark-mode', dark ? 'enabled' : 'disabled');
        });
    }

    // ----- Sidebar drawer (mobile/tablet) -----
    const sideBar = document.querySelector('.sidebar');
    const backdrop = document.querySelector('.backdrop');
    const menuBtn = document.getElementById('menu-btn');
    function setSidebar(open) {
        if (!sideBar) return;
        sideBar.classList.toggle('open', open);
        if (backdrop) backdrop.classList.toggle('open', open);
        if (menuBtn) menuBtn.setAttribute('aria-expanded', String(open));
    }
    if (menuBtn) menuBtn.addEventListener('click', () => setSidebar(!sideBar.classList.contains('open')));
    const closeBtn = document.getElementById('close-btn');
    if (closeBtn) closeBtn.addEventListener('click', () => setSidebar(false));
    if (backdrop) backdrop.addEventListener('click', () => setSidebar(false));

    // ----- User dropdown -----
    const userBtn = document.getElementById('user-btn');
    const dropdown = document.getElementById('user-dropdown');
    if (userBtn && dropdown) {
        userBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const open = dropdown.classList.toggle('open');
            userBtn.setAttribute('aria-expanded', String(open));
        });
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('open');
                userBtn.setAttribute('aria-expanded', 'false');
            }
        });
    }

    // ----- Mobile search toggle -----
    const searchBtn = document.getElementById('search-btn');
    const searchForm = document.querySelector('.search-form');
    if (searchBtn && searchForm) {
        searchBtn.addEventListener('click', () => {
            searchForm.classList.toggle('open');
            if (searchForm.classList.contains('open')) searchForm.querySelector('input').focus();
        });
    }

    // ----- Client-side course search (filters cards on the current page) -----
    if (searchForm) {
        const input = searchForm.querySelector('input');
        searchForm.addEventListener('submit', (e) => e.preventDefault());
        input.addEventListener('input', () => {
            const q = input.value.trim().toLowerCase();
            const cards = document.querySelectorAll('[data-search]');
            let shown = 0;
            cards.forEach((card) => {
                const match = card.dataset.search.toLowerCase().includes(q);
                card.hidden = !match;
                if (match) shown++;
            });
            const empty = document.getElementById('search-empty');
            if (empty) empty.hidden = shown !== 0 || cards.length === 0;
        });
    }

    // ----- Escape closes overlays -----
    document.addEventListener('keydown', (e) => {
        if (e.key !== 'Escape') return;
        setSidebar(false);
        if (dropdown) dropdown.classList.remove('open');
        if (searchForm) searchForm.classList.remove('open');
    });

    // ----- Dismissible alerts -----
    document.querySelectorAll('.alert .close').forEach((btn) => {
        btn.addEventListener('click', () => btn.closest('.alert').remove());
    });
})();

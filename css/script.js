let toggleBtn = document.getElementById('toggle-btn');
    let body = document.body;
    let darkMode = localStorage.getItem('dark-mode');

    const enableDarkMode = () => {
        toggleBtn.classList.replace('fa-sun', 'fa-moon');
        body.classList.add('dark');
        localStorage.setItem('dark-mode', 'enabled');
    }

    const disableDarkMode = () => {
        toggleBtn.classList.replace('fa-moon', 'fa-sun');
        body.classList.remove('dark');
        localStorage.setItem('dark-mode', 'disabled');
    }

    if (darkMode === 'enabled') {
        enableDarkMode();
    }

    toggleBtn.onclick = () => {
        darkMode = localStorage.getItem('dark-mode');
        if (darkMode === 'disabled') {
            enableDarkMode();
        } else {
            disableDarkMode();
        }
    }

    let profile = document.querySelector('.header .flex .profile');
    let search = document.querySelector('.header .flex .search-form');
    let sideBar = document.querySelector('.side-bar');

    document.querySelector('#user-btn').onclick = () => {
        profile.classList.toggle('active');
        search.classList.remove('active');
    }

    document.querySelector('#search-btn').onclick = () => {
        search.classList.toggle('active');
        profile.classList.remove('active');
    }

    document.querySelector('#menu-btn').onclick = () => {
        sideBar.classList.toggle('active');
        body.classList.toggle('active');
    }

    document.querySelector('#close-btn').onclick = () => {
        sideBar.classList.remove('active');
        body.classList.remove('active');
    }

    window.onscroll = () => {
        profile.classList.remove('active');
        search.classList.remove('active');
        if (window.innerWidth < 1200) {
            sideBar.classList.remove('active');
            body.classList.remove('active');
        }
    }

    const pdfFiles = {
        cpp: "cpp.pdf",
        backend: "backend(1).pdf",
        devops: "devops.pdf",
        devrel: "devrel.pdf",
    };
    
    const viewers = {};
    
    function loadPDF(viewerId, pdfPath) {
        let currentPage = 1;
        const scale = 1.2;
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");
    
        const viewer = document.getElementById(viewerId);
        viewer.innerHTML = ""; // Clear existing content
        viewer.appendChild(canvas);
    
        pdfjsLib.getDocument(pdfPath).promise.then((pdf) => {
            viewers[viewerId] = pdf;
            renderPage();
    
            function renderPage() {
                pdf.getPage(currentPage).then((page) => {
                    const viewport = page.getViewport({ scale });
                    canvas.width = viewport.width;
                    canvas.height = viewport.height;
    
                    const renderContext = {
                        canvasContext: ctx,
                        viewport,
                    };
                    page.render(renderContext);
                });
            }
    
            document.getElementById(`prev-${viewerId}`).addEventListener("click", () => {
                if (currentPage > 1) {
                    currentPage--;
                    renderPage();
                }
            });
    
            document.getElementById(`next-${viewerId}`).addEventListener("click", () => {
                if (currentPage < pdf.numPages) {
                    currentPage++;
                    renderPage();
                }
            });
        });
    }
    
    document.addEventListener("DOMContentLoaded", () => {
        for (const [id, file] of Object.entries(pdfFiles)) {
            loadPDF(`${id}-viewer`, file);
        }
    });
    
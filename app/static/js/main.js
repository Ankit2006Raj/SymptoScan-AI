document.addEventListener('DOMContentLoaded', () => {
    // Navbar scroll effect
    const navbar = document.getElementById('navbar');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Reveal animations on scroll
    function reveal() {
        var reveals = document.querySelectorAll('.reveal');

        for (var i = 0; i < reveals.length; i++) {
            var windowHeight = window.innerHeight;
            var elementTop = reveals[i].getBoundingClientRect().top;
            var elementVisible = 100;

            if (elementTop < windowHeight - elementVisible) {
                reveals[i].classList.add('active');
            }
        }
    }

    window.addEventListener('scroll', reveal);
    reveal(); // Trigger on load

    // Mobile menu toggle
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Number counter animation (for stats)
    const counters = document.querySelectorAll('.counter');
    let hasCounted = false;

    function countUp() {
        if(hasCounted) return;
        
        const statsSection = document.getElementById('stats-section');
        if(!statsSection) return;

        const sectionTop = statsSection.getBoundingClientRect().top;
        if(sectionTop < window.innerHeight) {
            hasCounted = true;
            counters.forEach(counter => {
                const target = +counter.getAttribute('data-target');
                const isFloat = counter.getAttribute('data-float') === 'true';
                const duration = 2000; // ms
                const increment = target / (duration / 16); // 60fps
                
                let current = 0;
                const updateCounter = () => {
                    current += increment;
                    if(current < target) {
                        counter.innerText = isFloat ? current.toFixed(1) : Math.ceil(current);
                        requestAnimationFrame(updateCounter);
                    } else {
                        counter.innerText = isFloat ? target.toFixed(1) : target;
                    }
                };
                updateCounter();
            });
        }
    }

    window.addEventListener('scroll', countUp);
    countUp(); // Check on load
});

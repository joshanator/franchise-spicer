/**
 * Enhanced JavaScript for Madden Franchise Event Generator
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add page load animation
    document.body.style.opacity = '0';
    requestAnimationFrame(() => {
        document.body.style.transition = 'opacity 0.3s ease';
        document.body.style.opacity = '1';
    });

    // Auto-hide flash messages with nice animation
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(function(flash, index) {
        // Stagger the entrance animation
        flash.style.animationDelay = `${index * 0.1}s`;
        
        setTimeout(function() {
            flash.style.transition = 'all 0.5s ease';
            flash.style.opacity = '0';
            flash.style.transform = 'translateX(20px)';
            setTimeout(function() {
                flash.remove();
            }, 500);
        }, 5000 + (index * 500));
    });

    // Confirm before clearing history with custom styling
    const clearHistoryForms = document.querySelectorAll('form[action*="clear_history"]');
    clearHistoryForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to clear all history?\n\nThis action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Enhanced roll button with loading state
    const rollForms = document.querySelectorAll('form[action*="roll"]');
    rollForms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const btn = form.querySelector('.btn-roll');
            if (btn) {
                btn.innerHTML = '<span class="roll-text">Rolling</span><span class="roll-dots"></span>';
                btn.disabled = true;
                btn.style.pointerEvents = 'none';
                
                // Add rolling animation
                let dots = 0;
                const dotsEl = btn.querySelector('.roll-dots');
                const interval = setInterval(() => {
                    dots = (dots + 1) % 4;
                    dotsEl.textContent = '.'.repeat(dots);
                }, 300);
                
                // Clean up after navigation
                setTimeout(() => clearInterval(interval), 5000);
            }
        });
    });

    // Keyboard shortcuts with visual feedback
    const shortcuts = {
        'r': { selector: '.btn-roll', description: 'Roll for Event' },
        'a': { selector: 'form[action*="accept"] button', description: 'Accept Event' },
        's': { selector: 'form[action*="save"] button', description: 'Save' }
    };

    document.addEventListener('keydown', function(e) {
        // Don't trigger shortcuts when typing in inputs
        const activeElement = document.activeElement;
        const isInput = activeElement.tagName === 'INPUT' || 
                       activeElement.tagName === 'TEXTAREA' || 
                       activeElement.tagName === 'SELECT';
        
        if (isInput || e.ctrlKey || e.metaKey || e.altKey) return;
        
        const shortcut = shortcuts[e.key.toLowerCase()];
        if (shortcut) {
            const element = document.querySelector(shortcut.selector);
            if (element && !element.disabled) {
                e.preventDefault();
                
                // Visual feedback
                element.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    element.style.transform = '';
                    element.click();
                }, 100);
            }
        }
    });

    // Animate cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.card').forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = `all 0.5s ease ${index * 0.1}s`;
        observer.observe(card);
    });

    // Animate history entries
    document.querySelectorAll('.history-entry').forEach((entry, index) => {
        entry.style.opacity = '0';
        entry.style.transform = 'translateX(-20px)';
        entry.style.transition = `all 0.4s ease ${index * 0.05}s`;
        
        requestAnimationFrame(() => {
            entry.style.opacity = '1';
            entry.style.transform = 'translateX(0)';
        });
    });

    // Add ripple effect to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const ripple = document.createElement('span');
            ripple.style.cssText = `
                position: absolute;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                pointer-events: none;
                width: 100px;
                height: 100px;
                left: ${x - 50}px;
                top: ${y - 50}px;
                transform: scale(0);
                animation: ripple 0.6s ease-out;
            `;
            
            button.style.position = 'relative';
            button.style.overflow = 'hidden';
            button.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // Add CSS for ripple animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .roll-dots {
            display: inline-block;
            width: 24px;
            text-align: left;
        }
    `;
    document.head.appendChild(style);

    // Smooth form transitions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            // Add a subtle fade to the page content
            document.querySelector('main').style.transition = 'opacity 0.2s ease';
            document.querySelector('main').style.opacity = '0.7';
        });
    });

    // Option buttons hover enhancement
    document.querySelectorAll('.btn-option').forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 0 20px rgba(155, 35, 53, 0.2)';
        });
        btn.addEventListener('mouseleave', function() {
            this.style.boxShadow = '';
        });
    });

    // Active nav indicator animation
    const activeNav = document.querySelector('nav a.active');
    if (activeNav) {
        activeNav.style.animation = 'pulse 2s ease infinite';
    }

    // Add pulse animation
    const pulseStyle = document.createElement('style');
    pulseStyle.textContent = `
        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(155, 35, 53, 0.4); }
            50% { box-shadow: 0 0 0 4px rgba(155, 35, 53, 0); }
        }
    `;
    document.head.appendChild(pulseStyle);

    // Console easter egg
    console.log('%c🏈 Madden Franchise Event Generator', 'font-size: 20px; font-weight: bold; color: #9b2335;');
    console.log('%cLightweight Edition', 'font-size: 14px; color: #c9a227;');
    console.log('Keyboard shortcuts: R = Roll, A = Accept, S = Save');
});

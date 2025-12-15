/* Performance Optimizations - Додайте цей файл до всіх сторінок */

/* Image lazy loading */
document.addEventListener('DOMContentLoaded', () => {
    // Lazy loading для зображень
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
    
    // Prefetch для критичних ресурсів при hover
    const links = document.querySelectorAll('a[href^="/"]');
    links.forEach(link => {
        link.addEventListener('mouseenter', () => {
            const prefetchLink = document.createElement('link');
            prefetchLink.rel = 'prefetch';
            prefetchLink.href = link.href;
            document.head.appendChild(prefetchLink);
        }, { once: true });
    });
});

/* Debounce функція для оптимізації подій */
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

/* Throttle функція для оптимізації scroll подій */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/* LocalStorage кеш для даних меню */
const MenuCache = {
    set(key, data, ttl = 300000) { // 5 хвилин за замовчуванням
        const item = {
            data: data,
            expiry: Date.now() + ttl
        };
        try {
            localStorage.setItem(key, JSON.stringify(item));
        } catch (e) {
            console.warn('localStorage not available', e);
        }
    },
    
    get(key) {
        try {
            const itemStr = localStorage.getItem(key);
            if (!itemStr) return null;
            
            const item = JSON.parse(itemStr);
            if (Date.now() > item.expiry) {
                localStorage.removeItem(key);
                return null;
            }
            return item.data;
        } catch (e) {
            return null;
        }
    },
    
    clear() {
        try {
            localStorage.clear();
        } catch (e) {
            console.warn('localStorage not available', e);
        }
    }
};

/* Service Worker для offline підтримки */
if ('serviceWorker' in navigator && window.location.protocol === 'https:') {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then(reg => console.log('Service Worker registered'))
            .catch(err => console.log('Service Worker registration failed'));
    });
}

/* Оптимізація форм з валідацією на клієнті */
function optimizeForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    // Real-time валідація з debounce
    const inputs = form.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        const validateInput = debounce(() => {
            if (input.validity.valid) {
                input.classList.remove('invalid');
                input.classList.add('valid');
            } else {
                input.classList.remove('valid');
                input.classList.add('invalid');
            }
        }, 300);
        
        input.addEventListener('input', validateInput);
    });
    
    // Попередження перед закриттям з незбереженими даними
    let formDirty = false;
    inputs.forEach(input => {
        input.addEventListener('input', () => { formDirty = true; }, { once: true });
    });
    
    window.addEventListener('beforeunload', (e) => {
        if (formDirty) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
    
    form.addEventListener('submit', () => { formDirty = false; });
}

/* Performance metrics */
if (window.performance && window.performance.timing) {
    window.addEventListener('load', () => {
        setTimeout(() => {
            const perfData = window.performance.timing;
            const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
            console.log(`Page load time: ${pageLoadTime}ms`);
            
            // Можна відправити метрики на сервер
            if (pageLoadTime > 3000) {
                console.warn('Page load time is slow!');
            }
        }, 0);
    });
}

/* Оптимізація скролу */
let ticking = false;
function onScroll() {
    if (!ticking) {
        window.requestAnimationFrame(() => {
            // Ваша логіка обробки скролу
            ticking = false;
        });
        ticking = true;
    }
}

window.addEventListener('scroll', onScroll, { passive: true });

/* Preconnect до зовнішніх ресурсів */
function addPreconnect(url) {
    const link = document.createElement('link');
    link.rel = 'preconnect';
    link.href = url;
    document.head.appendChild(link);
}

// Приклад: якщо використовуєте зовнішні CDN
// addPreconnect('https://cdn.example.com');

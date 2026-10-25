(() => {
  'use strict';

  const ready = (callback) => {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', callback, { once: true });
    else callback();
  };

  ready(() => {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // A subtle page progress line makes long articles easier to navigate.
    const progress = document.createElement('div');
    progress.className = 'bx-site-progress';
    progress.setAttribute('aria-hidden', 'true');
    document.body.appendChild(progress);

    let scheduled = false;
    const updateScrollUI = () => {
      const scrollable = document.documentElement.scrollHeight - window.innerHeight;
      const percent = scrollable > 0 ? Math.min(100, Math.max(0, window.scrollY / scrollable * 100)) : 0;
      progress.style.width = percent + '%';
      backTop.classList.toggle('is-visible', window.scrollY > 480);
      scheduled = false;
    };
    const requestScrollUpdate = () => {
      if (scheduled) return;
      scheduled = true;
      window.requestAnimationFrame(updateScrollUI);
    };

    const backTop = document.createElement('button');
    backTop.className = 'bx-back-top';
    backTop.type = 'button';
    backTop.setAttribute('aria-label', '返回页面顶部');
    backTop.setAttribute('title', '返回顶部');
    backTop.innerHTML = '<span aria-hidden="true">↑</span>';
    backTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' }));
    document.body.appendChild(backTop);
    window.addEventListener('scroll', requestScrollUpdate, { passive: true });
    window.addEventListener('resize', requestScrollUpdate, { passive: true });
    updateScrollUI();

    // Reading-time hint based on visible article text, with a conservative Chinese reading pace.
    const article = document.querySelector('.post-single .post-content');
    const meta = document.querySelector('.post-single .post-meta');
    if (article && meta && !meta.querySelector('.bx-reading-time')) {
      const text = (article.innerText || article.textContent || '').replace(/\s+/g, '');
      const chineseChars = (text.match(/[\u3400-\u9fff]/g) || []).length;
      const latinWords = (text.match(/[A-Za-z0-9_+#.-]+/g) || []).length;
      const minutes = Math.max(1, Math.ceil(chineseChars / 450 + latinWords / 180));
      const hint = document.createElement('span');
      hint.className = 'bx-reading-time';
      hint.textContent = '· 约 ' + minutes + ' 分钟阅读';
      meta.appendChild(hint);
    }

    // Accessible image lightbox for article/project illustrations; no third-party dependency.
    const mediaRoot = document.querySelector('.post-single .post-content, .project-detail__content');
    if (mediaRoot) {
      const images = Array.from(mediaRoot.querySelectorAll('img')).filter((image) => !image.closest('a'));
      if (images.length) {
        const lightbox = document.createElement('div');
        lightbox.className = 'bx-lightbox';
        lightbox.setAttribute('role', 'dialog');
        lightbox.setAttribute('aria-modal', 'true');
        lightbox.setAttribute('aria-label', '图片预览');
        lightbox.innerHTML = '<button class="bx-lightbox__close" type="button" aria-label="关闭图片预览">×</button><img alt="">';
        document.body.appendChild(lightbox);
        const preview = lightbox.querySelector('img');
        const close = lightbox.querySelector('button');
        let previousFocus = null;

        const closeLightbox = () => {
          if (!lightbox.classList.contains('is-open')) return;
          lightbox.classList.remove('is-open');
          document.body.classList.remove('bx-lightbox-open');
          preview.removeAttribute('src');
          previousFocus?.focus?.();
        };
        const openLightbox = (image) => {
          previousFocus = image;
          preview.src = image.currentSrc || image.src;
          preview.alt = image.alt || '文章图片';
          lightbox.classList.add('is-open');
          document.body.classList.add('bx-lightbox-open');
          close.focus();
        };

        images.forEach((image) => {
          image.tabIndex = 0;
          image.setAttribute('role', 'button');
          image.setAttribute('aria-label', (image.alt || '打开图片') + '（放大查看）');
          image.addEventListener('click', () => openLightbox(image));
          image.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
              event.preventDefault();
              openLightbox(image);
            }
          });
        });
        close.addEventListener('click', closeLightbox);
        lightbox.addEventListener('click', (event) => {
          if (event.target === lightbox) closeLightbox();
        });
        document.addEventListener('keydown', (event) => {
          if (event.key === 'Escape') closeLightbox();
          if (event.key === 'Tab' && lightbox.classList.contains('is-open')) {
            event.preventDefault();
            close.focus();
          }
        });
      }
    }

    // Add subtle entrance reveal only where supported; content remains visible without JS.
    if (!reduceMotion && 'IntersectionObserver' in window) {
      const revealTargets = document.querySelectorAll('.bx-project-card, .project-archive-card, .bx-learning-card, .bx-stats-card');
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('bx-in-view');
          observer.unobserve(entry.target);
        });
      }, { threshold: 0.08 });
      revealTargets.forEach((element) => {
        element.classList.add('bx-reveal-ready');
        observer.observe(element);
      });
    }
  });
})();

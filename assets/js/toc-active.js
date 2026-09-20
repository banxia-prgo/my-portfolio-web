document.addEventListener('DOMContentLoaded', () => {
  const toc = document.querySelector('.post-single .toc');
  const content = document.querySelector('.post-single .post-content');

  if (!toc || !content) return;

  const links = Array.from(toc.querySelectorAll('a[href^="#"]'));
  const headings = links
    .map((link) => {
      const id = decodeURIComponent(link.getAttribute('href').slice(1));
      return document.getElementById(id);
    })
    .filter(Boolean);

  if (!headings.length) return;

  const desktopQuery = window.matchMedia('(min-width: 1451px)');
  const root = document.documentElement;
  const minWidth = 180;
  const maxWidth = 380;
  const gap = 40;

  const ensureResizeHandle = () => {
    if (!desktopQuery.matches || toc.querySelector('.toc-resize-handle')) return;

    const handle = document.createElement('span');
    handle.className = 'toc-resize-handle';
    handle.setAttribute('role', 'separator');
    handle.setAttribute('aria-label', '调整目录宽度');
    handle.setAttribute('aria-orientation', 'vertical');
    handle.tabIndex = 0;
    toc.appendChild(handle);

    let dragging = false;

    const getLeft = () => toc.getBoundingClientRect().left;
    const setWidth = (width) => {
      const nextWidth = Math.max(minWidth, Math.min(maxWidth, width));
      root.style.setProperty('--toc-sidebar-width', `${nextWidth}px`);
      root.style.setProperty('--toc-sidebar-gap', `${gap}px`);
      handle.setAttribute('aria-valuenow', String(Math.round(nextWidth)));
    };

    const onMove = (event) => {
      if (!dragging) return;
      setWidth(event.clientX - getLeft());
    };

    const stopDragging = () => {
      dragging = false;
      handle.classList.remove('is-dragging');
      document.body.classList.remove('toc-is-resizing');
      document.removeEventListener('pointermove', onMove);
      document.removeEventListener('pointerup', stopDragging);
    };

    handle.addEventListener('pointerdown', (event) => {
      if (!desktopQuery.matches) return;
      dragging = true;
      handle.classList.add('is-dragging');
      document.body.classList.add('toc-is-resizing');
      handle.setPointerCapture?.(event.pointerId);
      document.addEventListener('pointermove', onMove);
      document.addEventListener('pointerup', stopDragging, { once: true });
      event.preventDefault();
    });

    handle.addEventListener('keydown', (event) => {
      if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
      const current = parseFloat(getComputedStyle(root).getPropertyValue('--toc-sidebar-width')) || 220;
      setWidth(current + (event.key === 'ArrowRight' ? 10 : -10));
      event.preventDefault();
    });
  };

  const setActive = (heading) => {
    links.forEach((link) => {
      const id = decodeURIComponent(link.getAttribute('href').slice(1));
      const active = heading && id === heading.id;
      link.classList.toggle('toc-active', active);
      const item = link.closest('li');
      item?.classList.toggle('toc-active-item', active);

      if (active && item) {
        const tocBox = toc.getBoundingClientRect();
        const itemBox = item.getBoundingClientRect();
        const outsideAbove = itemBox.top < tocBox.top;
        const outsideBelow = itemBox.bottom > tocBox.bottom;
        if (outsideAbove || outsideBelow) {
          item.scrollIntoView({ block: 'nearest', inline: 'nearest', behavior: 'smooth' });
        }
      }
    });
  };

  let currentHeading = headings[0];
  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);

      if (visible.length) {
        currentHeading = visible[0].target;
      } else {
        const passed = headings.filter((heading) => heading.getBoundingClientRect().top <= 140);
        currentHeading = passed[passed.length - 1] || headings[0];
      }

      setActive(currentHeading);
    },
    {
      rootMargin: '-110px 0px -65% 0px',
      threshold: [0, 1]
    }
  );

  headings.forEach((heading) => observer.observe(heading));
  setActive(currentHeading);
  ensureResizeHandle();

  desktopQuery.addEventListener?.('change', () => {
    if (desktopQuery.matches) ensureResizeHandle();
  });

  links.forEach((link) => {
    link.addEventListener('click', () => {
      const id = decodeURIComponent(link.getAttribute('href').slice(1));
      const heading = document.getElementById(id);
      if (heading) setActive(heading);
    });
  });
});

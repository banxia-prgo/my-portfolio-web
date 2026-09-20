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

  const setActive = (heading) => {
    links.forEach((link) => {
      const id = decodeURIComponent(link.getAttribute('href').slice(1));
      const active = heading && id === heading.id;
      link.classList.toggle('toc-active', active);
      link.closest('li')?.classList.toggle('toc-active-item', active);
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

  links.forEach((link) => {
    link.addEventListener('click', () => {
      const id = decodeURIComponent(link.getAttribute('href').slice(1));
      const heading = document.getElementById(id);
      if (heading) setActive(heading);
    });
  });
});

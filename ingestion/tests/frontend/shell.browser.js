(() => {
  const links = Array.from(document.querySelectorAll('.app-nav a'));
  const toggle = document.getElementById('nav-toggle');
  const before = toggle.getAttribute('aria-expanded'); toggle.click();
  const changed = toggle.getAttribute('aria-expanded') !== before; toggle.click();
  return {screen: document.body.dataset.screen, width: innerWidth, height: innerHeight, horizontalOverflow: document.documentElement.scrollWidth > innerWidth, navigationLinks: links.length, currentLinks: links.filter(link => link.hasAttribute('aria-current')).length, toggleWorks: changed, sidebarPosition: getComputedStyle(document.querySelector('.app-sidebar')).position, textFont: getComputedStyle(document.body).fontFamily, heading: document.querySelector('h1')?.textContent, minimumControlHeight: Math.min(...Array.from(document.querySelectorAll('button:not([disabled]),input:not([type=checkbox]),select')).filter(node => node.offsetParent !== null).map(node => node.getBoundingClientRect().height))};
})()

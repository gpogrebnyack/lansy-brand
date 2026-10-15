// The top bar, one for every page: Core (the main page), the four techniques, then the tools: the Lab (the pen and the blobs) and the Canvas. Include it right after <body>:
// <script src="nav.js"></script> (from labs/: ../nav.js). It finds the site root from its own src, marks the current page, and stays
// out of the lab's exports (?solo, ?shape) and the canvas. On the main page Canvas is the flip button (index.html runs it); elsewhere
// it opens the main page already turned to the canvas.
(() => {
  const q = new URLSearchParams(location.search);
  if (q.has('solo') || q.has('shape') || q.has('clean') || window !== top) return;   // not in exports, nor in the canvas the main page holds in a frame
  const root = new URL('.', document.currentScript.src).href;
  const here = location.pathname.split('/').pop().replace(/\.html$/, '') || 'index';
  const ico = {
    lab: '<path d="M17.5 21C15.567 21 14 19.433 14 17.5L14 3L21 3L21 17.5C21 19.433 19.433 21 17.5 21Z"/><path d="M22 3L13 3"/><path d="M17 7H14"/><path d="M10 16.875C10 19.9126 8 21 6 21C4 21 2 19.9126 2 16.875C2 13.8374 6 10 6 10C6 10 10 13.8374 10 16.875Z"/><path d="M14 12C15.083 11.1336 16.2974 9.87843 17.771 10.7626C19.0014 11.5009 20.0342 10.7244 21 10"/>',   // Hugeicons labs
    canvas: '<path d="M20.4371 12.5061C23.4219 7.00258 22.0614 3.26685 16.9548 3C13.2433 3.07086 9.41471 5.07063 6.35871 8.16433C3.79408 10.7606 1.26891 14.479 2.1959 18.018C2.40059 18.7994 2.79969 19.3318 3.43015 19.8328C5.12441 21.1791 6.7874 21.2976 9.99031 20.5113C13.2339 19.5257 15.2448 18.0408 16.9404 16.5217M16.9404 16.5217C16.9421 16.5201 16.9439 16.5185 16.9457 16.5169C16.9489 16.5141 16.9468 16.5087 16.9425 16.5087C16.9393 16.5087 16.937 16.512 16.9381 16.515C16.9389 16.5173 16.9396 16.5195 16.9404 16.5217ZM16.9404 16.5217C17.3108 17.6169 17.0762 18.5944 16.4385 20.5113"/>',
  };
  const svg = k => `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ico[k]}</svg>`;
  const link = (id, href, text, icon) => `<a href="${root}${href}"${id === here ? ' class="on" aria-current="page"' : ''}>${icon ? svg(icon) : ''}${text}</a>`;
  const css = document.createElement('style');
  css.textContent = `
.tb{position:fixed;top:16px;left:50%;transform:translateX(-50%);z-index:10;display:flex;align-items:center;gap:4px;padding:6px;border-radius:999px;
  background:rgba(255,255,255,.72);-webkit-backdrop-filter:blur(19px) saturate(1.4);backdrop-filter:blur(19px) saturate(1.4);box-shadow:inset 0 0 0 1px rgba(32,31,29,.06),0 12px 32px -20px rgba(32,31,29,.25)}
.tb a,.tb .flip{display:inline-flex;align-items:center;gap:6px;padding:8px 12px;border:0;border-radius:999px;background:none;font:400 15px/1.55 Struve,sans-serif;color:#75736F;text-decoration:none;white-space:nowrap;cursor:pointer;outline:none}
.tb a:hover,.tb .flip:hover{background:rgba(32,31,29,.05);color:#201F1D}
.tb a.on,.tb .flip[aria-pressed=true]{background:#201F1D;color:#FFFFFF}
.tb a:focus-visible,.tb .flip:focus-visible{box-shadow:0 0 0 2px #201F1D}
.tb svg{flex:none}.tb .flip svg{transition:transform .6s cubic-bezier(.65,0,.35,1)}.tb .flip[aria-pressed=true] svg{transform:rotate(180deg)}
.tb .sep{flex:none;width:1px;height:20px;margin:0 6px;background:rgba(32,31,29,.12)}   /* the labs: tools, not rules */
@media (max-width:900px){.tb{top:10px;max-width:calc(100% - 20px);overflow-x:auto;scrollbar-width:none}.tb::-webkit-scrollbar{display:none}.tb a,.tb .flip{font-size:14px;padding:7px 10px}}`;
  document.head.appendChild(css);
  const nav = document.createElement('nav');
  nav.className = 'tb'; nav.setAttribute('aria-label', 'Pages');
  nav.innerHTML = link('index', 'index.html', 'Core') + link('marker', 'marker.html', 'Marker') + link('blob', 'blob.html', 'Blob')
    + link('dots', 'dots.html', 'Dots') + link('3d', '3d.html', '3D') + '<span class="sep" aria-hidden="true"></span>'
    + link('line-lab', 'labs/line-lab.html', 'Lab', 'lab')
    + (here === 'index' ? `<button class="flip" aria-pressed="false">${svg('canvas')}Canvas</button>` : `<a href="${root}index.html?view=canvas"${here === 'canvas' ? ' class="on" aria-current="page"' : ''}>${svg('canvas')}Canvas</a>`);
  document.body.prepend(nav);
})();

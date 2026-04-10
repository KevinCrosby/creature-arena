/*! coi-serviceworker — enables SharedArrayBuffer on GitHub Pages
 *  Adds COOP/COEP headers via Service Worker so crossOriginIsolated = true.
 *  Inspired by github.com/nickerso/coi-serviceworker (MIT). */

if (typeof window === 'undefined') {
  /* ---- Service Worker context ---- */
  self.addEventListener('install', () => self.skipWaiting());
  self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));

  self.addEventListener('fetch', (e) => {
    if (e.request.cache === 'only-if-cached' && e.request.mode !== 'same-origin') return;

    e.respondWith(
      fetch(e.request)
        .then((r) => {
          if (r.status === 0) return r;          // opaque
          const h = new Headers(r.headers);
          h.set('Cross-Origin-Embedder-Policy',
            r.headers.get('Cross-Origin-Embedder-Policy') || 'credentialless');
          h.set('Cross-Origin-Opener-Policy',
            r.headers.get('Cross-Origin-Opener-Policy') || 'same-origin');
          return new Response(r.body, { status: r.status, statusText: r.statusText, headers: h });
        })
        .catch((err) => {
          console.error('COI fetch error:', err);
          return fetch(e.request);               // fall through without headers
        })
    );
  });

} else {
  /* ---- Window context — register SW ---- */
  (async () => {
    const tag = 'coi-reload';
    const reloaded = window.sessionStorage.getItem(tag);
    window.sessionStorage.removeItem(tag);
    if (window.crossOriginIsolated) return;       // already good
    if (reloaded) return;                         // avoid infinite reload
    if (!window.isSecureContext) return;

    try {
      const reg = await navigator.serviceWorker.register(
        new URL(document.currentScript.src).pathname);
      if (reg.active && !navigator.serviceWorker.controller) {
        window.sessionStorage.setItem(tag, '1');
        window.location.reload();
      } else if (reg.installing) {
        reg.installing.addEventListener('statechange', function () {
          if (this.state === 'activated') {
            window.sessionStorage.setItem(tag, '1');
            window.location.reload();
          }
        });
      }
    } catch (err) {
      console.error('COI SW registration failed:', err);
    }
  })();
}

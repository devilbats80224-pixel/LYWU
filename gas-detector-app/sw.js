self.addEventListener('install', event => {
  event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    try {
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter(key => /gas-(detector|leak-response)-offline-v/i.test(key))
          .map(key => caches.delete(key))
      );
    } catch (_) {}

    try {
      await self.registration.unregister();
    } catch (_) {}

    const clients = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
    for (const client of clients) {
      try {
        client.navigate(client.url);
      } catch (_) {}
    }
  })());
});

self.addEventListener('fetch', () => {});

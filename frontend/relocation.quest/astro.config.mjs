import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
  integrations: [tailwind()],
  output: 'static',
  site: 'https://relocation.quest',

  // Build optimization
  vite: {
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor': ['@apollo/client', 'graphql'],
          },
        },
      },
    },
  },

  // Image optimization
  image: {
    service: {
      entrypoint: 'astro/assets/services/sharp',
    },
  },
});

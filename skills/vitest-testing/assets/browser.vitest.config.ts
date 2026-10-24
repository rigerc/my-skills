// Example real-browser setup. Requires @vitest/browser-playwright and Playwright browsers.
// Keep your existing framework Vite plugins if testing React/Vue/etc.
import { defineConfig } from 'vitest/config'
import { playwright } from '@vitest/browser-playwright'

export default defineConfig({
  test: {
    browser: {
      enabled: true,
      provider: playwright(),
      instances: [{ browser: 'chromium' }],
      headless: true,
    },
  },
})

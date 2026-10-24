// Example for a NEW project. Do not overwrite existing Vite/Vitest config.
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'node',
    // The default include pattern already finds *.test.* and *.spec.*.
    // Add setupFiles, include/exclude, and coverage only when needed.
  },
})

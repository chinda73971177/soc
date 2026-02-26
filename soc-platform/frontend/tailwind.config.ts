import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        soc: {
          bg: '#0a0e1a',
          panel: '#0f1629',
          border: '#1e2d4a',
          accent: '#00d4ff',
          green: '#00ff88',
          red: '#ff3366',
          orange: '#ff8c00',
          yellow: '#ffd700',
          purple: '#8b5cf6',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
} satisfies Config

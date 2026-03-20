/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Syne"', 'sans-serif'],
        body: ['"DM Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        ink: {
          950: '#0a0a0f',
          900: '#111118',
          800: '#1a1a26',
          700: '#242436',
          600: '#2e2e48',
        },
        pulse: {
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
        },
        acid: {
          400: '#4ade80',
          500: '#22c55e',
        },
        ember: {
          400: '#fb923c',
          500: '#f97316',
        },
        sky: {
          400: '#38bdf8',
        }
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease forwards',
        'slide-up': 'slideUp 0.35s ease forwards',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: 0 }, to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: 'translateY(12px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
      }
    }
  },
  plugins: []
}

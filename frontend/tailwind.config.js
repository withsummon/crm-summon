import frappeUIPreset from 'frappe-ui/tailwind'

export default {
  presets: [frappeUIPreset],
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/frappe-ui/src/**/*.{vue,js,ts,jsx,tsx}',
    '../node_modules/frappe-ui/src/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/frappe-ui/frappe/**/*.{vue,js,ts,jsx,tsx}',
    '../node_modules/frappe-ui/frappe/**/*.{vue,js,ts,jsx,tsx}',
  ],
  safelist: [{ pattern: /!(text|bg)-/, variants: ['hover', 'active'] }],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eaf6ff',
          100: '#d7edff',
          200: '#a9d9ff',
          300: '#73c0ff',
          400: '#38a4ff',
          500: '#007fee',
          600: '#0069d1',
          700: '#0642a3',
          800: '#083982',
          900: '#0a3168',
          DEFAULT: '#007fee',
        },
        summon: {
          black: '#0a0a0a',
          charcoal: '#161616',
          graphite: '#252525',
          blue: '#007fee',
          navy: '#0642a3',
          violet: '#7c3aed',
        },
        crm: {
          teal: '#008C95',
          'teal-dark': '#006B73',
          'teal-light': '#D9F3F4',
          'bni-orange': '#F37021',
          purple: '#b77cff',
          blue: '#6676ff',
          green: '#00A887',
          pink: '#ff5ec4',
          surface: '#F3F4F6',
          'surface-light': '#F8FAFC',
          text: '#111827',
          'text-secondary': '#6B7280',
          muted: '#9CA3AF',
          border: '#E5E7EB',
          warning: '#F59E0B',
          danger: '#EF4444',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Plus Jakarta Sans', 'Manrope', 'DM Sans', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

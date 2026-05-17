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
      },
      fontFamily: {
        sans: ['Poppins', 'Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

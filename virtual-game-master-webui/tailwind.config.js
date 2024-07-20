module.exports = {
  purge: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'],
  darkMode: false,
  theme: {
    extend: {
      colors: {
        gray: {
          900: '#121827',
          800: '#1F2937',
          700: '#374151',
          // ... add other shades as needed
        },
        indigo: {
          600: '#4F46E5',
          700: '#4338CA',
        },
      },
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
}
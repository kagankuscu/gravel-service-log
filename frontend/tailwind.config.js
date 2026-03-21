/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				gravel: {
					50: '#f9f7f4',
					100: '#f0ebe3',
					200: '#dfd5c5',
					300: '#cab89f',
					400: '#b49677',
					500: '#a07d5f',
					600: '#8a6754',
					700: '#735547',
					800: '#5e463d',
					900: '#4d3b35',
					950: '#291e1b'
				}
			}
		}
	},
	plugins: []
};

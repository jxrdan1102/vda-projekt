import type { Config } from 'tailwindcss';
import * as typography from '@tailwindcss/typography';
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],

	theme: {
		extend: {}
	},

	plugins: [typography]
} as Config;

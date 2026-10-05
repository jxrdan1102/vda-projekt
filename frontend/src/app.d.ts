// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		interface Locals {
			user: {
				sub: string;
				id: number;
				/** superadmin | admin | user | readonly */
				role: string;
				/** Firma des Nutzers, null beim Superadmin */
				company: number | null;
			} | null;
		}
		interface PageState {
			newModell?: any;
			newComponent?: any;
			updateComp?: any
			selectedConstant?: any
			kmgInfo?: any;
			componentInfo?: any;
			newModelPage?: any;
		}
		// interface Error {}
		// interface PageData {}
		// interface Platform {}
	}
}

export {};

import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ fetch, cookies }) => {
    try {
        // Refresh-Token im Backend verwerfen (Cookie wird von SvelteKit mitgeschickt)
        await fetch('http://localhost:9999/auth/logout', { method: 'POST', credentials: 'include' });
    } catch (e) {
        console.error('Logout im Backend fehlgeschlagen:', e);
    }
    cookies.delete('access_token', { path: '/' });
    cookies.delete('refresh_token', { path: '/' });
    throw redirect(303, '/login');
};

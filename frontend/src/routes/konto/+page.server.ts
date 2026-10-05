import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

const API = 'http://localhost:9999';

export const load: PageServerLoad = async ({ fetch }) => {
    const res = await fetch(`${API}/auth/me`, { credentials: 'include' });
    return { me: res.ok ? await res.json() : null };
};

export const actions: Actions = {
    changePassword: async ({ request, fetch }) => {
        const fd = await request.formData();
        const old_password = fd.get('old_password')?.toString() ?? '';
        const new_password = fd.get('new_password')?.toString() ?? '';
        const repeat = fd.get('new_password_repeat')?.toString() ?? '';
        if (new_password !== repeat) {
            return fail(400, { error: 'Die neuen Passwörter stimmen nicht überein' });
        }
        const res = await fetch(`${API}/auth/change_password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ old_password, new_password })
        });
        if (!res.ok) {
            const body = await res.json().catch(() => ({}));
            return fail(res.status, { error: body.detail ?? 'Passwort konnte nicht geändert werden' });
        }
        return { success: 'Passwort geändert' };
    }
};

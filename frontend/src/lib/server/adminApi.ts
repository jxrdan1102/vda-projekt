import { fail } from '@sveltejs/kit';

export const API = 'http://localhost:9999';

/** Aufruf ans Backend; die Auth-Cookies leitet SvelteKits fetch automatisch weiter */
export async function api(fetch: typeof globalThis.fetch, path: string, method = 'GET', body?: unknown) {
    return fetch(`${API}${path}`, {
        method,
        credentials: 'include',
        headers: body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
        body: body !== undefined ? JSON.stringify(body) : undefined
    });
}

/** JSON laden, bei Fehler Fallback zurückgeben */
export async function getJson<T>(fetch: typeof globalThis.fetch, path: string, fallback: T): Promise<T> {
    const res = await api(fetch, path);
    return res.ok ? ((await res.json()) as T) : fallback;
}

/** Backend-Antwort in ein Form-Action-Ergebnis übersetzen */
export async function actionResult(res: Response, success: string) {
    if (res.ok) return { success };
    const body = await res.json().catch(() => ({}));
    const detail = typeof body.detail === 'string' ? body.detail : 'Aktion fehlgeschlagen';
    return fail(res.status, { error: detail });
}

export const str = (fd: FormData, key: string) => fd.get(key)?.toString().trim() ?? '';

export const optInt = (fd: FormData, key: string) => {
    const v = str(fd, key);
    return v === '' ? null : Number(v);
};

export type { AdminCompany, AdminUser } from '$lib/roles';

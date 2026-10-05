import type { Actions, PageServerLoad } from './$types';
import { actionResult, api, getJson, optInt, str, type AdminCompany, type AdminUser } from '$lib/server/adminApi';

export const load: PageServerLoad = async ({ fetch, locals }) => {
    const isSuperadmin = locals.user?.role === 'superadmin';
    const [users, companies] = await Promise.all([
        getJson<AdminUser[]>(fetch, '/admin/users', []),
        isSuperadmin ? getJson<AdminCompany[]>(fetch, '/admin/companies', []) : Promise.resolve([])
    ]);
    return { users, companies, currentUserId: locals.user?.id ?? null };
};

export const actions: Actions = {
    create: async ({ request, fetch }) => {
        const fd = await request.formData();
        const res = await api(fetch, '/admin/users', 'POST', {
            username: str(fd, 'username'),
            password: str(fd, 'password'),
            role: str(fd, 'role') || 'user',
            fk_company: optInt(fd, 'fk_company')
        });
        return actionResult(res, 'Nutzer angelegt');
    },

    update: async ({ request, fetch }) => {
        const fd = await request.formData();
        const body: Record<string, unknown> = {};
        if (fd.has('role')) body.role = str(fd, 'role');
        if (fd.has('is_active')) body.is_active = str(fd, 'is_active') === 'true';
        if (fd.has('fk_company')) body.fk_company = optInt(fd, 'fk_company');
        const res = await api(fetch, `/admin/users/${str(fd, 'id')}`, 'PATCH', body);
        return actionResult(res, 'Nutzer gespeichert');
    },

    password: async ({ request, fetch }) => {
        const fd = await request.formData();
        const res = await api(fetch, `/admin/users/${str(fd, 'id')}/password`, 'POST', { password: str(fd, 'password') });
        return actionResult(res, 'Passwort gesetzt');
    },

    delete: async ({ request, fetch }) => {
        const fd = await request.formData();
        const res = await api(fetch, `/admin/users/${str(fd, 'id')}`, 'DELETE');
        return actionResult(res, 'Nutzer gelöscht');
    }
};

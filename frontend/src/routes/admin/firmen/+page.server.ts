import { redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { actionResult, api, getJson, str, type AdminCompany } from '$lib/server/adminApi';

export const load: PageServerLoad = async ({ fetch, locals }) => {
    if (locals.user?.role !== 'superadmin') throw redirect(303, '/admin');
    return { companies: await getJson<AdminCompany[]>(fetch, '/admin/companies', []) };
};

export const actions: Actions = {
    create: async ({ request, fetch }) => {
        const fd = await request.formData();
        const admin_username = str(fd, 'admin_username');
        const res = await api(fetch, '/admin/companies', 'POST', {
            name: str(fd, 'name'),
            admin_username: admin_username || null,
            admin_password: admin_username ? str(fd, 'admin_password') : null
        });
        return actionResult(res, 'Firma angelegt');
    },

    update: async ({ request, fetch }) => {
        const fd = await request.formData();
        const body: Record<string, unknown> = {};
        if (fd.has('name')) body.name = str(fd, 'name');
        if (fd.has('is_active')) body.is_active = str(fd, 'is_active') === 'true';
        const res = await api(fetch, `/admin/companies/${str(fd, 'id')}`, 'PATCH', body);
        return actionResult(res, 'Firma gespeichert');
    },

    delete: async ({ request, fetch }) => {
        const fd = await request.formData();
        const res = await api(fetch, `/admin/companies/${str(fd, 'id')}`, 'DELETE');
        return actionResult(res, 'Firma gelöscht');
    }
};

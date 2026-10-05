import type { PageServerLoad } from './$types';
import { getJson, type AdminCompany, type AdminUser } from '$lib/server/adminApi';

export const load: PageServerLoad = async ({ fetch, locals }) => {
    const isSuperadmin = locals.user?.role === 'superadmin';
    const [users, companies, me] = await Promise.all([
        getJson<AdminUser[]>(fetch, '/admin/users', []),
        isSuperadmin ? getJson<AdminCompany[]>(fetch, '/admin/companies', []) : Promise.resolve([]),
        getJson<{ company_name: string | null } | null>(fetch, '/auth/me', null)
    ]);
    return { users, companies, companyName: me?.company_name ?? null };
};

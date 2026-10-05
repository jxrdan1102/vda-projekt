import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
    // Zugriff ist bereits in hooks.server.ts auf admin/superadmin beschränkt
    return { isSuperadmin: locals.user?.role === 'superadmin' };
};

export const ROLE_LABELS: Record<string, string> = {
    superadmin: 'Superadmin',
    admin: 'Firmen-Admin',
    user: 'Nutzer',
    readonly: 'Nur lesen'
};

export const isAdminRole = (role: string | undefined | null) => role === 'admin' || role === 'superadmin';

export type AdminUser = {
    id: number;
    username: string;
    role: string;
    fk_company: number | null;
    company_name: string | null;
    is_active: boolean;
};

export type AdminCompany = { id: number; name: string; is_active: boolean; user_count: number };

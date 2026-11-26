import type { PageServerLoad } from './$types';

const API = 'http://localhost:9999';

async function getJson<T>(fetch: typeof globalThis.fetch, path: string, fallback: T): Promise<T> {
    try {
        const res = await fetch(`${API}${path}`);
        return res.ok ? ((await res.json()) as T) : fallback;
    } catch {
        return fallback;
    }
}

type Projekt = {
    id: number;
    name: string;
    creation: string | null;
    modify: string | null;
    modell: { name: string; aufgabe_modell: number | null };
};
type Modell = { id: number; is_builtin: boolean | null };

export const load: PageServerLoad = async ({ fetch }) => {
    const [me, projekte, modelle, kmgs] = await Promise.all([
        getJson<{ username: string; company_name: string | null } | null>(fetch, '/auth/me', null),
        getJson<Projekt[]>(fetch, '/anamu/r', []),
        getJson<Modell[]>(fetch, '/modells/r', []),
        getJson<unknown[]>(fetch, '/kmgs', [])
    ]);

    const zuletzt = [...projekte]
        .sort((a, b) => (b.modify ?? b.creation ?? '').localeCompare(a.modify ?? a.creation ?? ''))
        .slice(0, 5);

    return {
        me,
        anzahl: {
            projekte: projekte.length,
            modelle: modelle.length,
            eingebaut: modelle.filter((m) => m.is_builtin).length,
            kmgs: kmgs.length
        },
        zuletzt
    };
};

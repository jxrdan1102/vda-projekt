import type {Actions, PageServerLoad} from './$types';
import {fail, redirect} from '@sveltejs/kit';

export const load: PageServerLoad = async ({ params, fetch }) => {

    const res = await fetch(`http://localhost:9999/kmgs`);
    if (!res.ok) {
        throw new Error(`Fehler beim Laden des KMGs`);
    }
    const kmg = await res.json();
    console.log(kmg)
    return { kmg };
};

export const actions: Actions = {
    default: async ({ request, params, fetch }) => {
        const formData = await request.formData();

        function parseOptionalString(key: string): string | undefined {
            const value = formData.get(key);
            if (value === null || value === '') return undefined;
            return value.toString();
        }
        function parseOptionalInt(key: string): number | undefined {
            const value = formData.get(key);
            if (value === null || value === '') return undefined;
            const parsed = parseInt(value.toString());
            return isNaN(parsed) ? undefined : parsed;
        }
        function parseOptionalFloat(key: string): number | undefined {
            const val = formData.get(key);
            if (val === null || val === '') return undefined;
            const parsed = parseFloat(val.toString());
            return isNaN(parsed) ? undefined : parsed;
        }

        const payload: Record<string, any> = {};
        payload.kmg_ident = parseOptionalString('kmg_ident');
        payload.kmg_bez = parseOptionalString('kmg_bez');
        payload.kmg_a = parseOptionalFloat('kmg_a');
        payload.kmg_k = parseOptionalFloat('kmg_k');
        payload.kmg_uc = parseOptionalFloat('kmg_uc');
        payload.kmg_lt = parseOptionalFloat('kmg_lt');
        payload.kmg_alpham = parseOptionalFloat('kmg_alpham');
        payload.kmg_mpeml = parseOptionalFloat('kmg_mpeml');

        console.log("Formular-Daten", payload);  // Überprüfe die extrahierten Daten

// Rest des Codes bleibt gleich...

        const res = await fetch(`http://localhost:9999/kmgs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json();
            return fail(res.status, { error: err.detail || 'Fehler beim Erstellen des KMGs.' });
        }

        throw redirect(303, `/analyseprojekt/3D-${params.analyseprojektId}`);
    }
};

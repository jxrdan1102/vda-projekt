import type {Actions, PageServerLoad} from './$types';
import {fail, redirect} from '@sveltejs/kit';

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { anakonstId } = params;

    const res = await fetch(`http://localhost:9999/anamu/anakonst/${anakonstId}`);
    if (!res.ok) {
        throw new Error(`Fehler beim Laden der Komponente mit ID ${anakonstId}`);
    }
    const constant = await res.json();
    console.log(constant)
    return { constant };
};

export const actions: Actions = {
    default: async ({ request, params, fetch }) => {
        const { anakonstId } = params;
        const formData = await request.formData();

        function parseOptionalString(key: string): string | undefined {
            const value = formData.get(key);
            if (value === null || value === '') return undefined;
            return value.toString();
        }

        function parseOptionalFloat(key: string): number | undefined {
            const val = formData.get(key);
            if (val === null || val === '') return undefined;
            const parsed = parseFloat(val.toString());
            return isNaN(parsed) ? undefined : parsed;
        }

        const payload: Record<string, any> = {};

        payload.constval = parseOptionalFloat('constval');
        console.log(payload);
        const res = await fetch(`http://localhost:9999/anamu/anakonst/${anakonstId}/r`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json();
            return fail(res.status, { error: err.detail || 'Fehler beim Speichern der Konstante.' });
        }

        throw redirect(303, `/analyseprojekt/${params.analyseprojektId}`);
    }
};

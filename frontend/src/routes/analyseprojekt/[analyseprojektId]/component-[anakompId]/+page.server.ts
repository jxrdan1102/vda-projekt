import type {Actions, PageServerLoad} from './$types';
import {fail, redirect} from '@sveltejs/kit';

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { anakompId } = params;

    const res = await fetch(`http://localhost:9999/anamu/anakomp/${anakompId}`);
    if (!res.ok) {
        throw new Error(`Fehler beim Laden der Komponente mit ID ${anakompId}`);
    }

    const component = await res.json();
    return { component };
};

export const actions: Actions = {
    default: async ({ request, params, fetch }) => {
        const { anakompId } = params;
        const formData = await request.formData();

        function parseOptionalInt(key: string): number | undefined {
            const val = formData.get(key);
            if (val === null || val === '') return undefined;
            const parsed = parseInt(val.toString());
            return isNaN(parsed) ? undefined : parsed;
        }

        function parseOptionalFloat(key: string): number | undefined {
            const val = formData.get(key);
            if (val === null || val === '') return undefined;
            const parsed = parseFloat(val.toString());
            return isNaN(parsed) ? undefined : parsed;
        }
        const payload: Record<string, any> = {};

        payload.terml0 = parseOptionalFloat('terml0');
        payload.terml1 = parseOptionalFloat('terml1');
        payload.wertart = parseOptionalInt('wertart');
        payload.freigrad = parseOptionalInt('freigrad');
        payload.frei_n_1 = parseOptionalInt('frei_n_1');
        payload.verteilung = parseOptionalInt('verteilung');
        payload.remark = formData.get('remark')?.toString();
        console.log(payload);
        const res = await fetch(`http://localhost:9999/anamu/anakomp/${anakompId}/r`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json();
            return fail(res.status, { error: err.detail || 'Fehler beim Speichern der Komponente.' });
        }

        throw redirect(303, `/analyseprojekt/${params.analyseprojektId}`);
    }
};

import type {Actions, PageServerLoad} from './$types';
import {fail, redirect} from '@sveltejs/kit';

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { componentId } = params;

    const [res, textsRes] = await Promise.all([
        fetch(`http://localhost:9999/components/${componentId}`, {
            credentials: 'include'
        }),
        fetch(`http://localhost:9999/modells/modell-texts`, {
            credentials: 'include'
        })
    ]);

    if (!res.ok) {
        throw new Error(`Fehler beim Laden der Komponente mit ID ${componentId}`);
    }

    const component = await res.json();
    const texts = await textsRes.json();

    return { component, texts };
};

export const actions: Actions = {
    default: async ({ request, params, fetch }) => {
        const { componentId, modellId } = params;
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
            const parsed = parseFloat(val.toString().replace(',', '.')); // ← diese Änderung
            return isNaN(parsed) ? undefined : parsed;
        }

        const payload: Record<string, any> = {};

        payload.terml0 = parseOptionalFloat('terml0');
        payload.terml1 = parseOptionalFloat('terml1');
        payload.wertart = parseOptionalInt('wertart');
        payload.freigrad = parseOptionalInt('freigrad');
        payload.frei_n_1 = parseOptionalInt('frei_n_1');
        payload.verteilung = parseOptionalInt('verteilung');
        payload.kflags = parseOptionalInt('kflags');
        payload.modltxtid = formData.get('modltxtid')?.toString();

        console.log("payload",payload)
        const res = await fetch(`http://localhost:9999/components/${componentId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json();
            return fail(res.status, { error: err.detail || 'Fehler beim Speichern der Komponente.' });
        }

        const result = await res.json();
        throw redirect(303, `/modelle/${modellId}?edited=1`);
        return {
            success: true,
            message: result.detail || 'Komponente gespeichert.'
        };
    }
};

import type {Actions, PageServerLoad} from './$types';
import {fail, redirect} from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params, fetch }) => {

    const response = await fetch(`http://localhost:9999/components`, {
        method: 'GET',
        credentials: 'include'  // ← WICHTIG
    });
    const responseBody = await response.json();
    console.log(responseBody);
    return {
        title: 'Komponenten:',
        komponenten: responseBody
    }
}

export const actions: Actions = {
    default: async ({ request, fetch, params }) => {
        const formData = await request.formData();
        const { modellId } = params;

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
        const payload : Record<string, any> = {};
        payload.kompid = parseInt(formData.get('kompid')as string);
        payload.terml0 = parseOptionalFloat('terml0');
        payload.terml1 = parseOptionalFloat('terml1');
        payload.wertart = parseOptionalInt('wertart');
        payload.freigrad = parseOptionalInt('freigrad');
        payload.frei_n_1 = parseOptionalInt('frei_n_1');
        payload.verteilung = parseOptionalInt('verteilung');
        payload.kflags = parseOptionalInt('kflags');
        payload.modltxtid = parseOptionalInt('modltxtid');
        console.log(payload);

        const res = await fetch(`http://localhost:9999/modells/${modellId}/addComponent`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json();
            return fail(res.status, {
                error: err.detail || 'Fehler beim Hinzufügen'
            });
        }

        const result = await res.json();
        throw redirect(303, `/modelle/${modellId}`)
        return {
            success: true,
            message: result.detail
        };
    }
};

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
        function parseOptionalFloat(key: string): number | undefined {
            const val = formData.get(key);
            if (val === null || val === '') return undefined;
            const parsed = parseFloat(val.toString());
            return isNaN(parsed) ? undefined : parsed;
        }
        const payload = {
            kompid: parseInt(formData.get('kompid') as string),
            terml0: formData.get('terml0') ? parseOptionalFloat(formData.get('terml0') as string) : null,
            terml1: formData.get('terml1') ? parseOptionalFloat(formData.get('terml1') as string) : null
        };

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

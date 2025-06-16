import type {Actions} from './$types';
import {fail} from '@sveltejs/kit';


export const actions: Actions = {
    default: async ({ request, fetch, params }) => {
        const formData = await request.formData();
        const { kmgId } = params;
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

        const res = await fetch(`http://localhost:9999/modells/${kmgId}/addComponent`, {
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
        return {
            success: true,
            message: result.detail
        };
    }
};

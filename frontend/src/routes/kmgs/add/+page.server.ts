import type {Actions} from './$types';
import {fail} from '@sveltejs/kit';


export const actions: Actions = {
    default: async ({ request, fetch }) => {
        const formData = await request.formData();

        const payload = {
            aufgabe_modell: parseInt(formData.get('methode') as string),
            name: formData.get('name') as string,
            aufgabe: formData.get('aufgabe') ? parseInt(formData.get('aufgabe') as string) : null
        };

        const res = await fetch('http://localhost:9999/modells/r', {
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
                error: err.detail || 'Fehler beim Speichern'
            });
        }

        const result = await res.json();
        return {
            success: true,
            message: result.detail
        };
    }
};

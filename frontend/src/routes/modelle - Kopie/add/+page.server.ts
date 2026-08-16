import type {Actions} from './$types';
import {fail, redirect} from '@sveltejs/kit';


export const actions: Actions = {
    default: async ({ request, fetch, params }) => {
        const formData = await request.formData();
        const payload = {
            aufgabe_modell: parseInt(formData.get('aufgabe_modell') as string),
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
        let modell = await res.json();
        if (!res.ok) {
            const err = await res.json();
            return fail(res.status, {
                error: err.detail || 'Fehler beim Speichern'
            });
        }
        if (payload.aufgabe_modell === 3) {
            throw redirect(303, `http://localhost:5173/modelle/3D-${modell.id}`);
        }
    throw redirect(303, `http://localhost:5173/modelle/${modell.id}`);
    }
};

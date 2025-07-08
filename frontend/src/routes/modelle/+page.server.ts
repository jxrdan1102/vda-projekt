import type {Actions, PageServerLoad} from './$types';
import {fail, redirect} from '@sveltejs/kit';

export const load: PageServerLoad = async ({ fetch }) => {
    const response = await fetch('http://localhost:9999/modells/r', {
        method: 'GET',
        credentials: 'include'  // ← WICHTIG
    });
    const responseBody = await response.json();
    console.log(responseBody);
    return {
        title: 'Modelle',
        modelle: responseBody
    }
}

export const actions: Actions = {
    default: async ({ request, fetch }) => {
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

        if (!res.ok) {
            const err = await res.json();
            return fail(res.status, {
                error: err.detail || 'Fehler beim Speichern'
            });
        }

        const modell = await res.json();

        if (payload.aufgabe_modell === 3) {
            throw redirect(303, `/modelle/3D-${modell.id}`);
        }
        throw redirect(303, `/modelle/${modell.id}`);
    }
};
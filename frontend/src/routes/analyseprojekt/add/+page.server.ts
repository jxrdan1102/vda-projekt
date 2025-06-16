import type {Actions, PageServerLoad} from './$types';
import {fail} from '@sveltejs/kit';

export const load: PageServerLoad = async ({ fetch }) => {
    const res = await fetch('http://localhost:9999/modells/r', {
        credentials: 'include'
    });

    if (!res.ok) {
        return { models: [] };
    }

    const data = await res.json();
    return {
        models: data  // Passe ggf. an, falls du ein anderes Format bekommst
    };
};
export const actions: Actions = {
    default: async ({ request, fetch }) => {
        const formData = await request.formData();

        const payload = {
            name: formData.get('name') as string,
            fk_modell: parseInt(formData.get('modell') as string),
            aenderungszustand: formData.get('aenderungszustand') ? formData.get('aenderungszustand') as string : null
        };
        console.log(payload);
        const res = await fetch('http://localhost:9999/anamu/r', {
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

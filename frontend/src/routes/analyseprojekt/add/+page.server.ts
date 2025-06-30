import type {Actions, PageServerLoad} from './$types';
import {fail, redirect} from '@sveltejs/kit';

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
    default: async ({ request, fetch, params }) => {
        const formData = await request.formData();
        const aufgabeModell = parseInt(formData.get('aufgabe_modell') as string);
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
        let projekt = await res.json();
        console.log("Hierrrr",aufgabeModell);
        if (aufgabeModell == 3) {
            throw redirect(303, `http://localhost:5173/analyseprojekt/3D-${projekt.id}`);
        }
        throw redirect(303, `http://localhost:5173/analyseprojekt/${projekt.id}`);
    }
};

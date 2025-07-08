import type {PageServerLoad} from './$types';
import type {Actions} from "../../../.svelte-kit/types/src/routes/analyseprojekt/add/$types";
import {fail, redirect} from "@sveltejs/kit";

export const load: PageServerLoad = async ({ fetch }) => {
    const response = await fetch('http://localhost:9999/anamu/r', {
        method: 'GET',
        credentials: 'include'  // ← WICHTIG
    });
    const responseBody = await response.json();
    console.log(responseBody);
    return {
        title: 'Analyseprojekte',
        analyseprojekt: responseBody
    }
}

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

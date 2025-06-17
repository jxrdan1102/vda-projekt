import type {Actions, PageServerLoad} from './$types';
import {fail} from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { modellId } = params;

    const response = await fetch(`http://localhost:9999/modells/${modellId}/r`, {
        method: 'GET',
        credentials: 'include'  // ← WICHTIG
    });
    const responseBody = await response.json();
    console.log(responseBody);
    return {
        title: 'Messgerät:',
        modell: responseBody,
        modellId: modellId,
    }
}


export const actions: Actions = {
    default: async ({ params, request, fetch }) => {
        const { modellId } = params;
        const formData = await request.formData();

        function parseOptionalInt(key: string): number | undefined {
            const value = formData.get(key);
            if (value === null || value === '') return undefined;
            const parsed = parseInt(value.toString());
            return isNaN(parsed) ? undefined : parsed;
        }

        function parseOptionalString(key: string): string | undefined {
            const value = formData.get(key);
            if (value === null || value === '') return undefined;
            return value.toString();
        }

        // Payload mit allen Feldern aus deinem Modell, nur wenn vorhanden
        const payload: Record<string, any> = {};

        const name = parseOptionalString('name');
        if (name !== undefined) payload.name = name;

        const geo_me = parseOptionalInt('geo_me');
        if (geo_me !== undefined) payload.geo_me = geo_me;

        const geo_mo = parseOptionalInt('geo_mo');
        if (geo_mo !== undefined) payload.geo_mo = geo_mo;

        const geo_bn = parseOptionalInt('geo_bn');
        if (geo_bn !== undefined) payload.geo_bn = geo_bn;

        const methode = parseOptionalInt('methode');
        if (methode !== undefined) payload.methode = methode;

        payload.tsk_ausenmessung = formData.has('tsk_ausenmessung') ? 1 : 0;
        payload.tsk_innenmessung = formData.has('tsk_innenmessung') ? 1 : 0;
        payload.tsk_tiefenmessung = formData.has('tsk_tiefenmessung') ? 1 : 0;
        payload.tsk_hoehenmessung = formData.has('tsk_hoehenmessung') ? 1 : 0;
        payload.tsk_stufenmessung = formData.has('tsk_stufenmessung') ? 1 : 0;

        const aufgabe_modell = parseOptionalInt(formData.get('aufgabe_modell') as string);
        if (aufgabe_modell !== undefined) payload.aufgabe_modell = aufgabe_modell;

        const description = parseOptionalString('description');
        if (description !== undefined) payload.description = description;

        const formel = parseOptionalString('formel');
        if (formel !== undefined) payload.formel = formel;

        const formeldesc = parseOptionalString('formeldesc');
        if (formeldesc !== undefined) payload.formeldesc = formeldesc;

        console.log(payload);
        // Update an Backend senden
        const res = await fetch(`http://localhost:9999/modells/${modellId}/r`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
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



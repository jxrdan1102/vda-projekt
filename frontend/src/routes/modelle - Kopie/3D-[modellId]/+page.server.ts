import type {Actions, PageServerLoad} from './$types';
import {fail,redirect} from "@sveltejs/kit";

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

        const aufgabe_modell = parseOptionalInt('aufgabe_modell');
        if (aufgabe_modell !== undefined) payload.aufgabe_modell = aufgabe_modell;
console.log("aufgabe_modell:: ", aufgabe_modell);
        const aufgabe = parseOptionalInt('aufgabe');
        if (aufgabe !== undefined) payload.aufgabe = aufgabe;
        console.log("aufgabe", aufgabe);

        const bezug1 = parseOptionalString('Bezug1');
        if (bezug1 !== undefined) payload.Bezug1 = bezug1;

        const bezug2 = parseOptionalString('Bezug2');
        if (bezug2 !== undefined) payload.Bezug2 = bezug2;

        const element1 = parseOptionalString('Element1');
        if (element1 !== undefined) payload.Element1 = element1;

        const element2 = parseOptionalString('Element2');
        if (element2 !== undefined) payload.Element2 = element2;

        const punktmuster = parseOptionalInt('punktmuster');
        if (punktmuster !== undefined) payload.punktmuster = punktmuster;

        const description = parseOptionalString('description');
        if (description !== undefined) payload.description = description;

        const formel = parseOptionalString('formel');
        if (formel !== undefined) payload.formel = formel;

        const formeldesc = parseOptionalString('formeldesc');
        if (formeldesc !== undefined) payload.formeldesc = formeldesc;
        console.log("Taster 1: ",parseOptionalInt("taster"));
        const optionalIntFields = [
            'taster', 'merkmal', 'element',
            'punktmusterB1', 'tasterschaft1', 'tasterschaft2', 'artdesmasses',
            'punktmusterR1', 'punktmusterR2', 'taster1', 'taster2',
            'abstand', 'winkelE1', 'winkelE2'
        ];

        for (const key of optionalIntFields) {
            const val = parseOptionalInt(key);
            if (val !== undefined) {
                payload[key] = val;
            }
        }

        const actionType = formData.get('action');


        console.log("Senden",payload);
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

        if (actionType === 'close') {
            throw redirect(303, '/analyseprojekt'); // z.B. Übersicht
        }
        
        if (actionType === 'continue') {
            throw redirect(303, `/modelle`); // z.B. nächste Seite
        }

        return {
            success: true,
            message: result.detail
        };
    }
};



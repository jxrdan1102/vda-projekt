import type {Actions, PageServerLoad} from './$types';
import {fail} from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { kmgId } = params;

    const response = await fetch(`http://localhost:9999/modells/${kmgId}/r`, {
        method: 'GET',
        credentials: 'include'  // ← WICHTIG
    });
    const responseBody = await response.json();
    return {
        title: 'Messgerät:',
        kmg: responseBody
    }
}


export const actions: Actions = {
    default: async ({ params, request, fetch }) => {
        const { kmgId } = params;
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

        const tsk_ausenmessung = parseOptionalInt('tsk_ausenmessung');
        if (tsk_ausenmessung !== undefined) payload.tsk_ausenmessung = tsk_ausenmessung;

        const tsk_innenmessung = parseOptionalInt('tsk_innenmessung');
        if (tsk_innenmessung !== undefined) payload.tsk_innenmessung = tsk_innenmessung;

        const tsk_tiefenmessung = parseOptionalInt('tsk_tiefenmessung');
        if (tsk_tiefenmessung !== undefined) payload.tsk_tiefenmessung = tsk_tiefenmessung;

        const tsk_hoehenmessung = parseOptionalInt('tsk_hoehenmessung');
        if (tsk_hoehenmessung !== undefined) payload.tsk_hoehenmessung = tsk_hoehenmessung;

        const tsk_stufenmessung = parseOptionalInt('tsk_stufenmessung');
        if (tsk_stufenmessung !== undefined) payload.tsk_stufenmessung = tsk_stufenmessung;

        const formel = parseOptionalString('formel');
        if (formel !== undefined) payload.formel = formel;

        const formeldesc = parseOptionalString('formeldesc');
        if (formeldesc !== undefined) payload.formeldesc = formeldesc;

        console.log(payload);
        // Update an Backend senden
        const res = await fetch(`http://localhost:9999/modells/${kmgId}/r`, {
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

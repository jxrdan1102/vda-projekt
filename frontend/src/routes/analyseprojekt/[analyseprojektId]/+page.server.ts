import type {Actions, PageServerLoad} from './$types';
import {fail} from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { analyseprojektId } = params;

    const response = await fetch(`http://localhost:9999/anamu/${analyseprojektId}/r`, {
        method: 'GET',
        credentials: 'include'  // ← WICHTIG
    });
    const responseBody = await response.json();
    console.log(responseBody);
    return {
        title: 'Analyseprojekt:',
        analyseprojekt: responseBody
    }
}


export const actions: Actions = {
    speichern: async ({ params, request, fetch }) => {
        const { analyseprojektId } = params;
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

        const aenderungszustand = parseOptionalString('aenderungszustand');
        if (aenderungszustand !== undefined) payload.aenderungszustand = aenderungszustand;

        const identnr = parseOptionalString('identnr');
        if (identnr !== undefined) payload.identnr = identnr;

        const remark = parseOptionalString('remark');
        if (remark !== undefined) payload.remark = remark;
        console.log(payload);
        // Update an Backend senden
        const res = await fetch(`http://localhost:9999/anamu/${analyseprojektId}/r`, {
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
    },
    berechnen: async ({ params,request }) => {
        const { analyseprojektId } = params;
        const cookieHeader = request.headers.get('cookie');
        const res = await fetch(`http://localhost:9999/anamu/${analyseprojektId}/calc/r`, {
            method: 'GET',
            headers: {
                // Sende den Cookie-Header mit an die API
                cookie: cookieHeader ?? ''
            }
        });
        const result = await res.json();
        if (!res.ok) {
            return fail(500, { error: 'Berechnung fehlgeschlagen.' });
        }
        console.log(result);
        return { unsicherheit: result};
    }
};




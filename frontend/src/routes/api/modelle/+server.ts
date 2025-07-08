// src/routes/api/models/+server.ts
import {json} from '@sveltejs/kit';

export const GET = async ({ fetch, cookies }) => {
    console.log("API angekommen");
    const res = await fetch('http://localhost:9999/modells/r', {
        credentials: 'include',
        headers: {
            cookie: cookies.get('acces-token') ?? ''
        }
    });

    if (!res.ok) {
        return json([], { status: 200 }); // Gib leeres Array zurück, wenn Fehler
    }

    const data = await res.json();
    return json(data);
};

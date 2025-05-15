import {type Handle, redirect} from "@sveltejs/kit";
import {authenticateUser} from "$lib/server/auth";

export const handle: Handle = async ({ event, resolve }) => {
    event.locals.user = authenticateUser(event);
    // Schütze nur bestimmte Routen
    if (event.url.pathname.startsWith('/kmgs') && !event.locals.user) {
        throw redirect(303, '/');
    }

    // Beispiel: Admin-Check nur für bestimmte Seiten
    if (event.url.pathname.startsWith('/admin')) {
        const res = await event.fetch('http://localhost:9999/auth/admin', {
            credentials: 'include'
        });
        console.log(res)
        const isAdmin = res.ok && (await res.json()) === true;

        if (!isAdmin) {
            throw redirect(303,"/");
        }
    }

    return resolve(event);
};
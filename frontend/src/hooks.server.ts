import {type Handle, redirect} from '@sveltejs/kit';
import {sequence} from '@sveltejs/kit/hooks';
import {authenticateUser} from '$lib/server/auth';
import type {SerializeOptions} from "cookie";

export const handleAuth: Handle = async ({ event, resolve }) => {
    let user = authenticateUser(event);
    event.locals.user = user;
    console.log('was geht ab');

    if (!user) {
        const refreshToken = event.cookies.get('refresh_token');

        if (refreshToken) {
            const refreshRes = await event.fetch('http://localhost:9999/auth/refresh_token', {
                method: 'GET',
                headers: {
                    cookie: `refresh_token=${refreshToken}`
                }
            });

            if (refreshRes.ok) {
                const setCookieHeader = refreshRes.headers.get('set-cookie');

                if (setCookieHeader) {
                    const cookieStrings = setCookieHeader.split(/,(?=\s*\w+=)/);

                    for (const cookieString of cookieStrings) {
                        const parts = cookieString.split(';').map((p) => p.trim());
                        const [nameValue, ...attributes] = parts;
                        const [name, value] = nameValue.split('=');

                        const options: SerializeOptions & { path: string } = { path: '/' };

                        for (const attr of attributes) {
                            const [attrName, attrValue] = attr.split('=');
                            switch (attrName.toLowerCase()) {
                                case 'httponly':
                                    options.httpOnly = true;
                                    break;
                                case 'secure':
                                    options.secure = true;
                                    break;
                                case 'samesite':
                                    options.sameSite = (attrValue?.toLowerCase() as 'lax' | 'strict' | 'none') ?? 'lax';
                                    break;
                                case 'max-age':
                                    options.maxAge = parseInt(attrValue ?? '', 10);
                                    break;
                                case 'path':
                                    options.path = attrValue ?? '/';
                                    break;
                            }
                        }

                        event.cookies.set(name, value, options);
                    }

                    // 🧠 Nach erfolgreichem Refresh: User neu setzen
                    user = authenticateUser(event);
                    event.locals.user = user;
                }
            }
        }
    }

    return resolve(event);
};


// 2. Protection-Handle: Routen schützen und Admin-Check
export const handleProtect: Handle = async ({ event, resolve }) => {
    if (event.url.pathname.startsWith('/modelle') && !event.locals.user) {
        throw redirect(303, '/');
    }

    if (event.url.pathname.startsWith('/admin')) {
        const res = await event.fetch('http://localhost:9999/auth/admin', {
            credentials: 'include'
        });

        const isAdmin = res.ok && (await res.json()) === true;

        if (!isAdmin) {
            throw redirect(303, '/');
        }
    }

    return resolve(event);
};

export const handle = sequence(handleAuth, handleProtect);

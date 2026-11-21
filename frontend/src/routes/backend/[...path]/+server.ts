import type { RequestHandler } from './$types';

// Leitet alle Aufrufe von /backend/... an das FastAPI-Backend weiter.
const BACKEND = 'http://127.0.0.1:9999';

const proxy: RequestHandler = async ({ request, params, url, cookies }) => {
    const headers = new Headers(request.headers);
    headers.delete('host');
    // Cookies aus SvelteKit nehmen statt aus der Browser-Anfrage: Hat hooks.server.ts den
    // Login gerade erneuert, stehen nur dort die neuen Tokens.
    const cookie = cookies.getAll().map((c) => `${c.name}=${c.value}`).join('; ');
    if (cookie) headers.set('cookie', cookie);
    else headers.delete('cookie');

    const res = await fetch(`${BACKEND}/${params.path}${url.search}`, {
        method: request.method,
        headers,
        body: request.method === 'GET' || request.method === 'HEAD' ? undefined : await request.arrayBuffer(),
        redirect: 'manual'
    });

    const out = new Headers(res.headers);
    out.delete('content-encoding');
    out.delete('content-length');
    return new Response(res.body, { status: res.status, headers: out });
};

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
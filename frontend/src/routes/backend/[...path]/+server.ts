import type { RequestHandler } from './$types';

// Leitet alle Aufrufe von /backend/... an das FastAPI-Backend weiter.
const BACKEND = 'http://127.0.0.1:9999';

const proxy: RequestHandler = async ({ request, params, url }) => {
    const headers = new Headers(request.headers);
    headers.delete('host');

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
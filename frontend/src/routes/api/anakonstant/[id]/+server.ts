import type {RequestHandler} from '@sveltejs/kit';

export const POST: RequestHandler = async ({ request, params, cookies, locals }) => {
    const id = params.id;
    const data = await request.json();

    const token = cookies.get('access_token'); // oder locals.userToken o.ä.
    const cookieHeader = cookies.get('access_token') ? `access_token=${cookies.get('access_token')}` : '';

    const response = await fetch(`http://localhost:9999/anamu/anakonst/${id}/r`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            ...(cookieHeader ? { Cookie: cookieHeader } : {})
        },
        body: JSON.stringify(data),
    });

    // Antwort von FastAPI weiterreichen
    const body = await response.text();

    return new Response(body, {
        status: response.status,
        headers: { 'Content-Type': response.headers.get('Content-Type') || 'application/json' }
    });
};

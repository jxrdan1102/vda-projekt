import type {PageServerLoad} from "./$types"

export const load: PageServerLoad = async ({ params, locals, fetch }) => {
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
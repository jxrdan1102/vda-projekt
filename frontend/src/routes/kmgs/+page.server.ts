import type {PageServerLoad} from "./$types"

export const load: PageServerLoad = async ({ locals, fetch }) => {
    const response = await fetch('http://localhost:9999/modells/r', {
        method: 'GET',
        credentials: 'include'  // ← WICHTIG
    });
    const responseBody = await response.json();
    return {
        title: 'Messgeräte',
        kmg: responseBody
    }
}
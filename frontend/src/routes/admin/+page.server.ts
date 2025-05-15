import type {PageServerLoad} from "../../../.svelte-kit/types/src/routes/kmgs/$types";

export const load: PageServerLoad = async ({ locals, fetch }) => {
    const response = await fetch('http://localhost:9999/auth/admin', {
        method: 'GET',
        credentials: 'include'  // ← WICHTIG
    });
    const responseBody = await response.json();
    return {
        title: 'Messgeräte',
        kmg: responseBody
    }
}
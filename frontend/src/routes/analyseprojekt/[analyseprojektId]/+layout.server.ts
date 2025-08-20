import type {LayoutServerLoad} from './$types';

export const load: LayoutServerLoad = async ({ params, fetch }) => {
    const { analyseprojektId } = params;
    const response = await fetch(`http://localhost:9999/anamu/${analyseprojektId}/r`, {
        method: 'GET',
        credentials: 'include',
    });
    const analyseprojekt = await response.json();
    return { analyseprojekt };
};

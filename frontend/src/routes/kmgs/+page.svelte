<script lang="ts">
    import {onMount} from 'svelte';
    import {browser} from '$app/environment';
    import {goto} from '$app/navigation';

    type KMG = {
        kmg_ident: number;
        kmg_bez: string;
        kmg_a: number;
        kmg_k: number;
        kmg_lt: number;
        kmg_uc: number;
        kmg_alpham: number;
        kmg_mpeml: number;
        id: number;
    };

    let kmgs: KMG[] = [];
    let loading = true;
    let error = '';

    // Funktion zum Überprüfen, ob das JWT abgelaufen ist
    function isTokenExpired(token: string): boolean {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.exp < Math.floor(Date.now() / 1000); // exp ist in Sekunden
        } catch {
            return true;
        }
    }

    onMount(async () => {
        if (!browser) return;

        const token = localStorage.getItem('access_token');

        // Falls kein Token oder abgelaufen → Weiterleitung zur Login-Seite
        if (!token || isTokenExpired(token)) {
            goto('/');
            return;
        }

        try {
            const response = await fetch('http://localhost:9999/kmgs/', {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Fehler beim Laden der KMGs');
            }

            kmgs = await response.json();
        } catch (e) {
            error = e.message || 'Unbekannter Fehler';
        } finally {
            loading = false;
        }
    });
</script>

{#if loading}
    <p>Lädt...</p>
{:else if error}
    <p style="color: red">{error}</p>
{:else}
    <ul>
        {#each kmgs as kmg}
            <li>
                <strong>{kmg.kmg_bez}</strong><br />
                Ident: {kmg.kmg_ident} | A: {kmg.kmg_a} | K: {kmg.kmg_k} | LT: {kmg.kmg_lt}
            </li>
        {/each}
    </ul>
{/if}

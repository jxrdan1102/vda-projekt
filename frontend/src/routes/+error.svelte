<script lang="ts">
    import { page } from '$app/state';

    const info = $derived.by(() => {
        switch (page.status) {
            case 404:
                return {
                    titel: 'Nicht gefunden',
                    text: 'Diese Seite oder dieser Eintrag existiert nicht – oder du hast keinen Zugriff darauf.'
                };
            case 403:
                return { titel: 'Kein Zugriff', text: 'Für diese Seite fehlen dir die nötigen Rechte.' };
            case 401:
                return { titel: 'Nicht angemeldet', text: 'Bitte melde dich erneut an.' };
            default:
                return {
                    titel: 'Etwas ist schiefgelaufen',
                    text: 'Beim Laden ist ein Fehler aufgetreten. Bitte versuch es gleich noch einmal.'
                };
        }
    });
</script>

<div class="max-w-lg mx-auto mt-20 bg-white rounded border p-8 text-center">
    <div class="text-5xl font-semibold text-gray-300 mb-2">{page.status}</div>
    <h1 class="text-xl font-semibold text-gray-800 mb-2">{info.titel}</h1>
    <p class="text-sm text-gray-600 mb-6">{info.text}</p>
    <div class="flex justify-center gap-3 text-sm">
        <button class="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300" onclick={() => history.back()}>Zurück</button>
        {#if page.status === 401}
            <a href="/login" class="px-4 py-2 rounded bg-[#1f3b5e] text-white hover:bg-[#2a4d7a]">Zur Anmeldung</a>
        {:else}
            <a href="/dashboard" class="px-4 py-2 rounded bg-[#1f3b5e] text-white hover:bg-[#2a4d7a]">Zur Übersicht</a>
        {/if}
    </div>
</div>

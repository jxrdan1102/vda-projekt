<script lang="ts">
    import { toast } from '$lib/notify';

    let { analyseprojektId, class: klasse = '' }: { analyseprojektId: string | number; class?: string } = $props();

    let loading = $state(false);
    let menuOpen = $state(false);
    let root: HTMLDivElement;

    async function openReport(extended = false) {
        if (loading) return;
        menuOpen = false;
        loading = true;
        // Fenster sofort öffnen (sonst blockiert der Browser das Pop-up nach dem Warten)
        const win = window.open('', '_blank');
        win?.document.write('<p style="font-family:sans-serif;padding:2rem;color:#555">PDF-Bericht wird erstellt …</p>');
        try {
            const response = await fetch(
                `/backend/anamu/${analyseprojektId}/report?start_date=2024-01-01&end_date=2024-12-31&extended=${extended}`,
                { method: 'GET', credentials: 'include' }
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const url = window.URL.createObjectURL(await response.blob());
            if (win) win.location.href = url;
            else window.open(url);
        } catch {
            win?.close();
            toast.error('PDF-Bericht konnte nicht erstellt werden');
        } finally {
            loading = false;
        }
    }
</script>

<svelte:window onclick={(e) => { if (menuOpen && !root?.contains(e.target as Node)) menuOpen = false; }} />

<div bind:this={root} class="relative inline-block {klasse}">
    <div class="flex">
        <button
            type="button"
            onclick={() => openReport(false)}
            disabled={loading}
            class="bg-gray-600 text-white text-sm px-3 py-1 rounded-l hover:bg-gray-700 disabled:opacity-70 disabled:cursor-wait inline-flex items-center gap-2"
        >
            {#if loading}
                <span class="inline-block w-3 h-3 border-2 border-white/40 border-t-white rounded-full animate-spin" aria-hidden="true"></span>
                PDF wird erstellt …
            {:else}
                PDF-Bericht
            {/if}
        </button>
        <button
            type="button"
            onclick={() => (menuOpen = !menuOpen)}
            aria-label="Weitere Berichte"
            class="bg-gray-600 text-white text-sm px-2 py-1 rounded-r border-l border-gray-500 hover:bg-gray-700"
        >
            ▾
        </button>
    </div>
    {#if menuOpen}
        <div class="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded shadow-lg z-50 w-48">
            <button
                type="button"
                onclick={() => openReport(true)}
                class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            >
                Erweiterter Bericht
            </button>
        </div>
    {/if}
</div>

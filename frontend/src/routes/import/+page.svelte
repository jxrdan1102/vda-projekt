<script lang="ts">
    import { apiFetch } from '$lib/client/fetchHelper';

    let modellFile: File | null = null;
    let anamuFile: File | null = null;
    let loading = false;
    let modellResult: any = null;
    let anamuResult: any = null;
    let error = '';

    async function handleModellImport() {
        if (!modellFile) return;
        loading = true;
        error = '';
        modellResult = null;
        const formData = new FormData();
        formData.append('file', modellFile);
        try {
            const res = await apiFetch('/backend/import/modell-xml', {
                method: 'POST',
                body: formData,
            });
            const json = await res.json();
            if (!res.ok) error = json.detail || 'Fehler';
            else modellResult = json;
        } catch (e: any) {
            error = e.message;
        } finally {
            loading = false;
        }
    }

    async function handleAnamuImport() {
        if (!anamuFile) return;
        loading = true;
        error = '';
        anamuResult = null;
        const formData = new FormData();
        formData.append('file', anamuFile);
        try {
            const res = await apiFetch('/backend/import/anamu-xml', {
                method: 'POST',
                body: formData,
            });
            const json = await res.json();
            if (!res.ok) error = json.detail || 'Fehler';
            else anamuResult = json;
        } catch (e: any) {
            error = e.message;
        } finally {
            loading = false;
        }
    }
</script>

<section class="max-w-2xl mx-auto pt-8 space-y-6">
    <h1 class="text-lg font-semibold" style="color: #1f3b5e;">Import</h1>

    <!-- Modell Import -->
    <div class="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
        <h2 class="text-sm font-semibold" style="color: #1f3b5e;">1. Modelle importieren</h2>
        <div>
            <label class="block text-xs font-medium mb-1" style="color: #2B6CB0;">XML-Datei</label>
            <input type="file" accept=".xml"
                on:change={(e) => modellFile = (e.target as HTMLInputElement).files?.[0] ?? null}
                class="block w-full text-sm text-gray-600 file:mr-4 file:py-1.5 file:px-4 file:rounded file:border-0 file:text-sm file:font-medium file:text-white file:cursor-pointer"
                style="file:background-color: #1f3b5e;" />
        </div>
        <button on:click={handleModellImport} disabled={!modellFile || loading}
            class="px-5 py-2 text-sm text-white rounded disabled:opacity-40"
            style="background-color: #1f3b5e;">
            {loading ? 'Importiere...' : 'Modelle importieren'}
        </button>
        {#if modellResult}
            <div class="bg-green-50 border border-green-200 text-green-700 px-4 py-2 rounded text-sm space-y-1">
                <p class="font-medium">{modellResult.detail}</p>
                {#each modellResult.modelle as m}
                    <p class="text-xs">→ <strong>{m.name}</strong> ({m.typ}, {m.komponenten} Komponenten)</p>
                {/each}
            </div>
        {/if}
    </div>

    <!-- ANAMU Import -->
    <div class="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
        <h2 class="text-sm font-semibold" style="color: #1f3b5e;">2. Analyseprojekte importieren</h2>
        <p class="text-xs text-gray-500">Modelle müssen zuerst importiert worden sein.</p>
        <div>
            <label class="block text-xs font-medium mb-1" style="color: #2B6CB0;">XML-Datei</label>
            <input type="file" accept=".xml"
                on:change={(e) => anamuFile = (e.target as HTMLInputElement).files?.[0] ?? null}
                class="block w-full text-sm text-gray-600 file:mr-4 file:py-1.5 file:px-4 file:rounded file:border-0 file:text-sm file:font-medium file:text-white file:cursor-pointer"
                style="file:background-color: #1f3b5e;" />
        </div>
        <button on:click={handleAnamuImport} disabled={!anamuFile || loading}
            class="px-5 py-2 text-sm text-white rounded disabled:opacity-40"
            style="background-color: #1f3b5e;">
            {loading ? 'Importiere...' : 'Analyseprojekte importieren'}
        </button>
        {#if anamuResult}
            <div class="bg-green-50 border border-green-200 text-green-700 px-4 py-2 rounded text-sm space-y-1">
                <p class="font-medium">{anamuResult.detail}</p>
                {#each anamuResult.importiert as a}
                    <p class="text-xs">→ <strong>{a.name}</strong></p>
                {/each}
                {#if anamuResult.uebersprungen.length > 0}
                    <p class="font-medium text-amber-600 mt-2">Übersprungen:</p>
                    {#each anamuResult.uebersprungen as s}
                        <p class="text-xs text-amber-600">→ ID {s.old_anamu_id}: {s.grund}</p>
                    {/each}
                {/if}
            </div>
        {/if}
    </div>

    {#if error}
        <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded text-sm">
            {error}
        </div>
    {/if}
</section>
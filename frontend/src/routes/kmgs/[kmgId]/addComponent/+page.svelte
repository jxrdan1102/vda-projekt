<script lang="ts">
    import type {ActionData, PageData} from './$types';

    export let data: PageData;
    export let form: ActionData;
</script>

<h1 class="text-2xl font-bold mb-4">Neue KMG hinzufügen</h1>

<form method="POST" class="space-y-4 max-w-md">
    <div>
        <label for="kompid" class="block font-medium">Komponente</label>
        <input id="kompid" name="kompid" type="number" required class="w-full border rounded px-3 py-2" />
    </div>

    <div>
        <label for="modltxtid" class="block font-medium">Beschreibung</label>
        <input id="modltxtid" name="modltxtid" type="number" class="w-full border rounded px-3 py-2" />
    </div>

    <div>
        <label for="terml0" class="block font-medium">L0 längenunabhängiger Term</label>
        <input id="terml0" name="terml0" step="any" type="number" class="w-full border rounded px-3 py-2" />
    </div>

    <div>
        <label for="terml1" class="block font-medium">L1 längenunabhängiger Term</label>
        <input id="terml1" name="terml1" step="any" type="number" class="w-full border rounded px-3 py-2" />
    </div>

    <div>
        <label for="verteilung" class="block font-medium">Verteilung</label>
        <input id="verteilung" name="verteilung" type="number" class="w-full border rounded px-3 py-2" />
    </div>
    <div>
        <label for="freigrad" class="block font-medium">Freiheitsgrad</label>
        <input id="freigrad" name="freigrad" type="number" class="w-full border rounded px-3 py-2" />
    </div>
    <div>
        <label for="frei_n_1" class="block font-medium">(N-1)</label>
        <input id="frei_n_1" name="frei_n_1" type="number" class="w-full border rounded px-3 py-2" />
    </div>
    <div>
        <label for="wertart" class="block font-medium">Streuungsparameter</label>
        <input id="wertart" name="wertart" type="number" class="w-full border rounded px-3 py-2" />
    </div>
    <div>
        <label for="kflags" class="block font-medium">Vorkommen im Modell</label>
        <input id="kflags" name="kflags" type="number" class="w-full border rounded px-3 py-2" />
    </div>

    <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        Hinzufügen
    </button>
</form>

{#if form?.error}
    <p class="text-red-600 mt-4">{form.error}</p>
{:else if form?.message}
    <p class="text-green-600 mt-4">{form.message}</p>
{/if}

<script lang="ts">
    export let data: { komponenten: any };

    const komponenten = data.komponenten;
    let kompid: number | null = null;

    let terml0: number;
    let wertart: number;
    let kflags: number = 1;
    let modltxtid: number;
    let messpunkt_anzahl: number;

</script>
<form method="POST" class="text-sm bg-white space-y-3 max-w-md mx-auto">
    <h2 class="text-base font-semibold text-gray-800 mb-2">Komponente hinzufügen</h2>

    <div class="grid grid-cols-2 gap-2">
        <label for="kompid" class="flex flex-col">
            <span class="text-gray-600">Komponente</span>
        <select id="kompid" name="kompid" bind:value={kompid} required class="border px-2 py-1 text-sm">
            <option value="" disabled selected>Bitte Komponente wählen</option>
            {#each komponenten as komponente}
                <option value={komponente.id}>{komponente.id}: {komponente.name}</option>
            {/each}
        </select>
        </label>
    <label class="flex flex-col">
        <span class="text-gray-600">Standardabweichung</span>
        <input type="number" name="terml0" bind:value={terml0} step="any"
               class="border px-2 py-1 text-sm" />
    </label>

    <label class="flex flex-col">
        <span class="text-gray-600">Anzahl Messpunkte</span>
        <input type="number" name="messpunkt_anzahl" bind:value={messpunkt_anzahl} step="any"
               class="border px-2 py-1 text-sm" />
    </label>

    <label class="flex flex-col">
        <span class="text-gray-600">Wertart</span>
        <select
                id="wertart"
                name="wertart"
                bind:value={wertart}

                class="border px-2 py-1 text-sm"
        >
            <option value="" disabled selected>Bitte wählen</option>
            <option value="4">A</option>
            <option value="5">B</option>
        </select>
    </label>


        <label class="flex flex-col">
            <span class="text-gray-600">Häufigkeit</span>
            <input type="number" name="kflags" bind:value={kflags}
                   class="border px-2 py-1 text-sm" />
        </label>
    </div>

    <div>
        <label class="block text-gray-600 mb-1">Beschreibung</label>
        <select name="modltxtid" bind:value={modltxtid} class="w-full border px-2 py-1 text-sm">
            <option value={0} selected> Bitte wählen</option>
            <option value={1}>Das ist eine tolle Komponente</option>
            <option value={2}>Diese Komponente ist sehr nützlich</option>
        </select>
    </div>

    <div class="flex justify-end pt-2">
        <button type="submit"
                class="bg-gray-800 text-white text-sm px-4 py-1 rounded hover:bg-gray-700">
            Speichern
        </button>
    </div>
</form>

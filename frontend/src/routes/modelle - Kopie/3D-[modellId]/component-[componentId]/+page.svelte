<script lang="ts">
    export let data: { component: any };

    const comp = data.component;
    let terml0: number = comp.terml0 ?? '';
    let wertart: string = comp.wertart != null ? comp.wertart.toString(): '';
    let messpunkt_anzahl: number = comp.messpunkt_anzahl ?? '';
    let anzahl_messungen: number = comp.anzahl_messungen ?? '';
    $: methodeA = wertart === '4';
    let kflags: number = comp.kflags ?? 0;
    let modltxtid: number | null = comp.modltxtid ?? 0;

</script>

<form method="POST" class="text-sm bg-white space-y-3 max-w-md mx-auto">
    <h2 class="text-base font-semibold text-gray-800 mb-2">Komponente bearbeiten</h2>

    <div class="grid grid-cols-2 gap-2">

        <label class="flex flex-col">
            <span class="text-gray-600">Methode</span>
            <select
                    id="wertart"
                    name="wertart"
                    bind:value={wertart}

                    class="border px-2 py-1 text-sm"
            >
                <option value="" disabled>Bitte wählen</option>
                <option value="4">A</option>
                <option value="5">B</option>

            </select>
        </label>

        <label class="flex flex-col">
            <span class="text-gray-600">Anzahl Messpunkte</span>
            <input type="number" name="messpunkt_anzahl" bind:value={messpunkt_anzahl} step="any"
                   class="border px-2 py-1 text-sm" />
        </label>

        {#if methodeA}
        <label class="flex flex-col">
            <span class="text-gray-600">Anzahl Messungen</span>
            <input type="number" name="anzahl_messungen" bind:value={anzahl_messungen} step="any"
                   class="border px-2 py-1 text-sm" />
        </label>
        {/if}
    </div>

    {#if methodeA}
        <div>
                <label class="flex flex-col">
                    <span class="text-gray-600">Standardabweichung der Messreihe</span>
                    <input type="number" name="terml0" bind:value={terml0} step="any"
                           class="border px-2 py-1 text-sm" />
                </label>
        </div>
    {/if}
    {#if !methodeA}
        <div>
                <label class="flex flex-col">
                    <span class="text-gray-600">Standardabweichung am Ausgleichselement</span>
                    <input type="number" name="terml0" bind:value={terml0} step="any"
                           class="border px-2 py-1 text-sm" />
                </label>
        </div>
    {/if}
        <label class="flex flex-col">
            <span class="text-gray-600">Häufigkeit</span>
            <input type="number" name="kflags" bind:value={kflags}
                   class="border px-2 py-1 text-sm" />
        </label>

    <div>
        <label class="block text-gray-600 mb-1">Beschreibung</label>
        <select name="modltxtid" bind:value={modltxtid} class="w-full border px-2 py-1 text-sm">
            <option value={0}>Bitte wählen</option>  <!-- für leer -->
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

<script lang="ts">
    export let data: { component: any };

    const comp = data.component;

    let terml0: number = comp.terml0 ?? 0;
    let terml1: number = comp.terml1 ?? 0;
    let wertart: string = comp.wertart != null ? comp.wertart.toString(): '';
    let freigrad: string = comp.freigrad != null ? comp.freigrad.toString() : '';
    let frei_n_1: number = comp.frei_n_1 ?? 0;
    let verteilung: string = comp.verteilung != null ? comp.verteilung.toString() : '';
    let kflags: number = comp.kflags ?? 0;
    let modltxtid: string = comp.modltxtid ?? '';
</script>

<form method="POST" class="text-sm bg-white space-y-3 max-w-md mx-auto">
    <h2 class="text-base font-semibold text-gray-800 mb-2">Komponente bearbeiten</h2>

    <div class="grid grid-cols-2 gap-2">
        <label class="flex flex-col">
            <span class="text-gray-600">Term L0</span>
            <input type="number" name="terml0" bind:value={terml0} step="any"
                   class="border px-2 py-1 text-sm" />
        </label>

        <label class="flex flex-col">
            <span class="text-gray-600">Term L1</span>
            <input type="number" name="terml1" bind:value={terml1} step="any"
                   class="border px-2 py-1 text-sm" />
        </label>

        <label class="flex flex-col">
            <span class="text-gray-600">Wertart</span>
            <select
                    id="wertart"
                    name="wertart"
                    bind:value={wertart}
                    required
                    class="border px-2 py-1 text-sm"
            >
                <option value="" disabled selected>Bitte wählen</option>
                <option value="1">Halbweite</option>
                <option value="2">Spannweite</option>
                <option value="3">Standardabweichung</option>
            </select>
        </label>

        <label class="flex flex-col">
            <span class="text-gray-600">Freiheitsgrad</span>
            <select
                    id="freigrad"
                    name="freigrad"
                    bind:value={freigrad}
                    required
                    class="border px-2 py-1 text-sm"
            >
                <option value="" disabled selected>Bitte wählen</option>
                <option value="1">Unbegrenzt</option>
                <option value="2">N-1</option>
            </select>
        </label>

        <label class="flex flex-col">
            <span class="text-gray-600">Frei n-1</span>
            <input type="number" name="frei_n_1" bind:value={frei_n_1}
                   class="border px-2 py-1 text-sm" />
        </label>

        <label class="flex flex-col">
            <span class="text-gray-600">Verteilung</span>
            <select
                    id="verteilung"
                    name="verteilung"
                    bind:value={verteilung}
                    required
                    class="border px-2 py-1 text-sm"
            >
                <option value="" disabled selected>Bitte wählen</option>
                <option value="1">Rechteckverteilung</option>
                <option value="2">Normalverteilung</option>
                <option value="3">Dreieckverteilung</option>
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
        <input type="text" name="modltxtid" bind:value={modltxtid}
               class="w-full border px-2 py-1 text-sm" />
    </div>

    <div class="flex justify-end pt-2">
        <button type="submit"
                class="bg-gray-800 text-white text-sm px-4 py-1 rounded hover:bg-gray-700">
            Speichern
        </button>
    </div>
</form>

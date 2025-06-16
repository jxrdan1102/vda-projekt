<script lang="ts">
    export let data: { component: any };

    const comp = data.component;

    let terml0: number = comp.terml0 ?? 0;
    let terml1: number = comp.terml1 ?? 0;
    let wertart: number = comp.wertart ?? 0;
    let freigrad: number = comp.freigrad ?? 0;
    let frei_n_1: number = comp.frei_n_1 ?? 0;
    let verteilung: number = comp.verteilung ?? 0;
    let kflags: number = comp.kflags ?? 0;
</script>

<form method="POST" class="max-w-xl mx-auto mt-10 p-6 border rounded shadow bg-white space-y-4">
    <h1 class="text-2xl font-bold text-blue-800">Komponente #{comp.kompid}</h1>

    <ul class="text-gray-700 space-y-2">
        <li><strong>Laufende Nr:</strong> {comp.lfdnr}</li>
        <li><strong>Modelltext ID:</strong> {comp.modltxtid ?? '—'}</li>

        <li>
            <label class="block font-semibold">Term L0:</label>
            <input type="number" name="terml0" bind:value={terml0} step="any" class="w-full border rounded px-3 py-2" />
        </li>

        <li>
            <label class="block font-semibold">Term L1:</label>
            <input type="number" name="terml1" bind:value={terml1} step="any" class="w-full border rounded px-3 py-2" />
        </li>

        <li>
            <label class="block font-semibold">Wertart:</label>
            <input type="number" name="wertart" bind:value={wertart} class="w-full border rounded px-3 py-2" />
        </li>

        <li>
            <label class="block font-semibold">Freiheitsgrad:</label>
            <input type="number" name="freigrad" bind:value={freigrad} class="w-full border rounded px-3 py-2" />
        </li>

        <li>
            <label class="block font-semibold">Frei n-1:</label>
            <input type="number" name="frei_n_1" bind:value={frei_n_1} class="w-full border rounded px-3 py-2" />
        </li>

        <li>
            <label class="block font-semibold">Verteilung:</label>
            <input type="number" name="verteilung" bind:value={verteilung} class="w-full border rounded px-3 py-2" />
        </li>

        <li>
            <label class="block font-semibold">Flags:</label>
            <input type="number" name="kflags" bind:value={kflags} class="w-full border rounded px-3 py-2" />
        </li>
    </ul>

    <button type="submit" class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
        Speichern
    </button>

    <a href="javascript:history.back()" class="inline-block mt-6 text-blue-600 hover:underline">
        ⬅ Zurück
    </a>
</form>

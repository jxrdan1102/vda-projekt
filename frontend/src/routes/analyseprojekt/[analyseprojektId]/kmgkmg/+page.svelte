<script lang="ts">
    export let data: { kmg: any[] };
    const kmg = data.kmg;

    let selectedKMG: any = kmg.length > 0 ? kmg[0] : null;
    let isCreatingNew = false;

    let kmg_ident = "";
    let kmg_bez = "";
    let kmg_a = 0;
    let kmg_k = 0;
    let kmg_lt = 0;
    let kmg_uc = 0;
    let kmg_alpham = 0;
    let kmg_mpeml = 0;

    function selectKMG(item: any) {
        selectedKMG = item;
        isCreatingNew = false;
        kmg_ident = item.kmg_ident ?? "";
        kmg_bez = item.kmg_bez ?? "";
        kmg_a = item.kmg_a ?? 0;
        kmg_k = item.kmg_k ?? 0;
        kmg_lt = item.kmg_lt ?? 0;
        kmg_uc = item.kmg_uc ?? 0;
        kmg_alpham = item.kmg_alpham ?? 0;
        kmg_mpeml = item.kmg_mpeml ?? 0;
    }

    function startNewKMG() {
        selectedKMG = null;
        isCreatingNew = true;
        kmg_ident = "";
        kmg_bez = "";
        kmg_a = 0;
        kmg_k = 0;
        kmg_lt = 0;
        kmg_uc = 0;
        kmg_alpham = 0;
        kmg_mpeml = 0;
    }
</script>

<div class="flex h-[80vh] rounded-xl bg-white shadow-lg overflow-hidden text-sm">
    <!-- Master-Liste -->
    <div class="w-1/3 border-r bg-gray-50 p-4 overflow-y-auto space-y-2">
        <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-semibold text-gray-800">KMGs</h2>
            <button on:click={startNewKMG} class="bg-indigo-600 text-white text-xs px-3 py-1.5 rounded-md shadow-sm hover:bg-indigo-500 transition">+ Neu</button>
        </div>
        {#each kmg as item (item.id)}
            <div class="relative border rounded-lg p-3 bg-white hover:bg-gray-50 cursor-pointer transition shadow-sm" class:selected={selectedKMG?.id === item.id}>
                <div on:click={() => selectKMG(item)} class="pr-5">
                    <div class="font-medium text-gray-900">{item.kmg_ident}</div>
                    <div class="text-gray-500 text-xs truncate">{item.kmg_bez}</div>
                </div>

                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="absolute top-2 right-2 w-4 h-4 text-gray-400 hover:text-gray-600 cursor-pointer" on:click|stopPropagation={() => deleteKMG(item.id)}>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                          d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                </svg>
            </div>

        {/each}
    </div>

    <!-- Detail-Bereich -->
    <div class="w-2/3 p-8 bg-white overflow-y-auto">
        <form method="POST" class="space-y-6 max-w-xl mx-auto">
            <div class="mb-4">
                <h2 class="text-lg font-semibold text-gray-800">
                    {isCreatingNew ? 'Neues KMG erstellen' : `KMG bearbeiten`}
                </h2>
            </div>

            <div class="grid grid-cols-2 gap-4">
                {#if isCreatingNew}
                    <div class="flex flex-col gap-1">
                        <label class="text-sm text-gray-600">KMG Ident</label>
                        <input type="text" bind:value={kmg_ident} name="kmg_ident" class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
                    </div>
                {/if}

                <div class="col-span-2 flex flex-col gap-1">
                    <label class="text-sm text-gray-600">Bezeichnung</label>
                    <input type="text" bind:value={kmg_bez} name="kmg_bez" class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>

                <div class="flex flex-col gap-1">
                    <label class="text-sm text-gray-600">A [µm]</label>
                    <input type="number" bind:value={kmg_a} name="kmg_a" step="any" class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>

                <div class="flex flex-col gap-1">
                    <label class="text-sm text-gray-600">K [µm/m]</label>
                    <input type="number" bind:value={kmg_k} name="kmg_k" step="any" class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>

                <div class="flex flex-col gap-1">
                    <label class="text-sm text-gray-600">LT [mm]</label>
                    <input type="number" bind:value={kmg_lt} name="kmg_lt" step="any" class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>

                <div class="flex flex-col gap-1">
                    <label class="text-sm text-gray-600">U(C) [µm]</label>
                    <input type="number" bind:value={kmg_uc} name="kmg_uc" step="any" class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>

                <div class="flex flex-col gap-1">
                    <label class="text-sm text-gray-600">Alpha M [10⁻⁶/K]</label>
                    <input type="number" bind:value={kmg_alpham} name="kmg_alpham" step="any" class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>

                <div class="flex flex-col gap-1">
                    <label class="text-sm text-gray-600">MPE(ML) [µm]</label>
                    <input type="number" bind:value={kmg_mpeml} name="kmg_mpeml" step="any" class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
            </div>

            <div class="flex justify-end pt-4">
                <button type="submit" class="bg-indigo-600 text-white px-5 py-2 rounded-md text-sm font-medium hover:bg-indigo-500 transition">Speichern</button>
            </div>
        </form>
    </div>
</div>

<style>
    .selected {
        background-color: #eef2ff;
        border-color: #6366f1;
    }
</style>
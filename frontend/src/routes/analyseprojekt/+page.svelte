<script lang="ts">
    import NewModelPage from './add/+page.svelte';
    import {page} from '$app/stores';
    import {goto, preloadData, pushState} from '$app/navigation';
    import Modal from "$lib/components/Modal.svelte";

    export let data;

    $: modellDialogOpen = !!$page.state?.newModell;

    async function onNewModellClick(e: MouseEvent & { currentTarget: HTMLAnchorElement }) {
        if (e.metaKey || e.ctrlKey) return;
        e.preventDefault();

        const { href } = e.currentTarget;
        const result = await preloadData(href);

        if (result.type === 'loaded' && result.status === 200) {
            pushState(href, { newModell: result.data });
        } else {
            goto(href);
        }
    }

    function closeModal() {
        history.back(); // entfernt state und schließt modal
    }
</script>

<div class="max-w-7xl mx-auto px-4 py-6">
    <!-- Page Header -->
    <div class="flex items-center gap-4 text-2xl font-semibold text-gray-600 mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-6">
            <path d="M19.5 21a3 3 0 0 0 3-3v-4.5a3 3 0 0 0-3-3h-15a3 3 0 0 0-3 3V18a3 3 0 0 0 3 3h15ZM1.5 10.146V6a3 3 0 0 1 3-3h5.379a2.25 2.25 0 0 1 1.59.659l2.122 2.121c.14.141.331.22.53.22H19.5a3 3 0 0 1 3 3v1.146A4.483 4.483 0 0 0 19.5 9h-15a4.483 4.483 0 0 0-3 1.146Z" />
        </svg>

        <span>Analyseprojekte</span>
    </div>

    <!-- Filter Row -->
    <div class="grid grid-cols-5 gap-2 mb-4">
        <input class="border rounded px-2 py-1" placeholder="Projekt" />
        <input class="border rounded px-2 py-1" placeholder="Änderungsstand" />
        <input class="border rounded px-2 py-1" placeholder="Modell" />
        <input class="border rounded px-2 py-1" placeholder="Identnummer" />
        <input class="border rounded px-2 py-1" placeholder="Datum" />
    </div>

    <!-- Table Header -->
    <div class="bg-gray-200 border border-gray-300 rounded-t-md flex items-center font-semibold px-4 py-2">
        <div class="w-1/2">Analyseprojekt</div>
        <div class="w-1/2">Änderungsstand</div>
        <div class="w-1/2">Identnummer</div>
        <div class="w-1/2 flex justify-between items-center">
            <span>Datum</span>
            <a href="/analyseprojekt/add" on:click={onNewModellClick} title="Neues Modell hinzufügen">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6 text-green-600 hover:scale-110 transition-transform">
                    <path fill-rule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25ZM12.75 9a.75.75 0 0 0-1.5 0v2.25H9a.75.75 0 0 0 0 1.5h2.25V15a.75.75 0 0 0 1.5 0v-2.25H15a.75.75 0 0 0 0-1.5h-2.25V9Z" clip-rule="evenodd" />
                </svg>
            </a>
        </div>
    </div>

    <!-- Table Body -->
    <div class="border border-t-0 border-gray-300 divide-y divide-gray-200">
        {#each data.analyseprojekt as analyseprojekt}
            <div class="flex px-4 py-1 hover:bg-gray-100 cursor-pointer" on:dblclick={() => goto(`/analyseprojekt/${analyseprojekt.id}`)}>
                <div class="w-1/2">{analyseprojekt.name}</div>
                <div class="w-1/2">{analyseprojekt.aenderungszustand}</div>
                <div class="w-1/2">{analyseprojekt.identnr}</div>
                <div class="w-1/2 flex justify-between items-center">
                    <span>{analyseprojekt.creation}</span>
                    <div class="flex gap-3">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-5 h-5 text-gray-500 hover:text-blue-500 cursor-pointer">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16.5 8.25V6a2.25 2.25 0 0 0-2.25-2.25H6A2.25 2.25 0 0 0 3.75 6v8.25A2.25 2.25 0 0 0 6 16.5h2.25m8.25-8.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-7.5A2.25 2.25 0 0 1 8.25 18v-1.5m8.25-8.25h-6a2.25 2.25 0 0 0-2.25 2.25v6" />
                        </svg>
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-5 h-5 text-red-500 hover:text-red-700 cursor-pointer">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                        </svg>
                    </div>
                </div>
            </div>
        {/each}
    </div>
</div>


<!-- Modal -->
<Modal open={modellDialogOpen} on:close={closeModal}>
    <NewModelPage data={$page.state.newModell} />
</Modal>

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

<div>
    <div class="max-w-5xl mx-auto">
        <h1 class="text-4xl font-bold text-blue-800 mb-8 border-b pb-2 border-blue-200">
            Modelle
            <a href="kmgs/add" on:click={onNewModellClick}>+</a>
        </h1>

        <!-- Hier Liste etc. -->
        <div class="grid gap-6 md:grid-cols-2">
            {#each data.kmg as kmg}
                <div class="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition-shadow duration-200">
                    <h2 class="text-lg font-semibold text-gray-800 mb-1">KMG #{kmg.id}</h2>
                    <p class="text-sm text-gray-600 mb-3">{kmg.name}</p>

                    <a
                            class="inline-block text-sm text-blue-700 font-medium hover:underline"
                            href={`/kmgs/${kmg.id}`}
                            data-sveltekit-preload-data="hover"
                    >
                        ➡ Mehr Details ansehen
                    </a>
                </div>
            {/each}
        </div>
    </div>
</div>

<!-- Modal -->
<Modal open={modellDialogOpen} on:close={closeModal}>
<NewModelPage data={$page.state.newModell} />
</Modal>

<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { COMPONENTS, Components } from '$lib/Mapping.js';

    export let components: any[] = [];
    export let editable: boolean = true;

    const ModelTextLabels: Record<number, string> = {
        0: '',
        1: 'Das ist eine tolle Komponente',
        2: 'Diese Komponente ist sehr nützlich',
    };

    let selectedRow: number | null = null;
    const dispatch = createEventDispatcher<{
        addComponent: MouseEvent;
        openComponent: { event: MouseEvent; compId: number };
        deleteComponent: number;
    }>();
</script>

<div class="border border-gray-300 rounded overflow-hidden bg-gray-200">
    <table class="w-full text-sm border-t">
        <thead class="bg-gray-200 text-gray-700">
            <tr>
                <th class="px-2 py-1 text-left w-1"></th>
                <th class="px-2 py-1 text-left">Komponente</th>
                <th class="px-2 py-1 text-left">Beschreibung</th>
                <th class="float-right p-1">
                    {#if editable}
                        <svg
                            on:click={(e) => dispatch('addComponent', e)}
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                            fill="currentColor"
                            class="size-5.5 hover:text-gray-800 cursor-pointer"
                        >
                            <path fill-rule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25ZM12.75 9a.75.75 0 0 0-1.5 0v2.25H9a.75.75 0 0 0 0 1.5h2.25V15a.75.75 0 0 0 1.5 0v-2.25H15a.75.75 0 0 0 0-1.5h-2.25V9Z" clip-rule="evenodd" />
                        </svg>
                    {/if}
                </th>
            </tr>
        </thead>
        <tbody>
            {#each components as comp, i}
                <tr
                    class="{selectedRow === i ? 'bg-cyan-800 text-white' : 'hover:bg-cyan-900 hover:text-white'} cursor-pointer"
                    on:click={() => (selectedRow = i)}
                    on:dblclick={(e) => {
                        if (editable) {
                            dispatch('openComponent', {
                                event: e,
                                compId: comp.id
                                });
                            }
                        }
                    }>
                    <td class="px-2 py-1 text-left w-0.5">{i + 1}</td>
                    <td class="px-2 py-1">{Components[comp.kompid] ? Components[comp.kompid] : COMPONENTS[comp.kompid]}</td>
                    <td class="px-2 py-1">{ModelTextLabels[comp.modltxtid] ?? ''}</td>
                    <td class="float-right px-1">
                        {#if editable}
                            <button type="button" on:click={() => dispatch('deleteComponent', comp.id)}>
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-5 h-5 text-red-500 hover:text-red-700 cursor-pointer">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                                </svg>
                            </button>
                        {/if}
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>

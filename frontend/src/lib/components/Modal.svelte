<script lang="ts">
    import {createEventDispatcher, onDestroy, onMount} from 'svelte';
    import {browser} from "$app/environment";

    export let open = false;
    const dispatch = createEventDispatcher();

    function onBackdropClick(e: MouseEvent) {
        if (e.target === e.currentTarget) {
            dispatch('close');
        }
    }

    function onKeyDown(e: KeyboardEvent) {
        if (e.key === 'Escape' && open) {
            dispatch('close');
        }
    }

    onMount(() => {
        if (browser) window.addEventListener('keydown', onKeyDown);
    });
    onDestroy(() => {
        if (browser) window.removeEventListener('keydown', onKeyDown);
    });
</script>

{#if open}
    <div class="fixed inset-0 bg-[rgba(0,0,0,0.5)] flex items-center justify-center z-50" role="dialog" aria-modal="true" on:click={onBackdropClick} tabindex="0" on:keydown={(e) => e.key === 'Enter' && dispatch('close')}>
        <div class="bg-white rounded-lg shadow-lg max-w-xl w-full relative p-6" on:pointerdown|stopPropagation>
            <button class="absolute top-2 right-2 text-gray-700 text-xl font-bold" aria-label="Close" on:click={() => dispatch('close')}>&times;</button>
            <slot />
        </div>
    </div>
{/if}

<script lang="ts">
    export let editable: boolean = true;
</script>

<button
    type="button"
    on:click={() => (editable = !editable)}
    class="flex items-center gap-1.5 text-xs px-3 py-1 rounded border transition-colors
        {editable
            ? 'bg-cyan-900 text-white border-cyan-900 hover:bg-cyan-950'
            : 'bg-white text-gray-600 border-gray-400 hover:bg-gray-100'}"
    title={editable ? 'Bearbeitung sperren' : 'Bearbeitung freigeben'}
>
    {#if editable}
        <!-- Unlock icon -->
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-3.5 h-3.5">
            <path d="M18 1.5c2.9 0 5.25 2.35 5.25 5.25v3.75a.75.75 0 0 1-1.5 0V6.75a3.75 3.75 0 1 0-7.5 0v3h.5a2.25 2.25 0 0 1 2.25 2.25V19.5a2.25 2.25 0 0 1-2.25 2.25H3.75A2.25 2.25 0 0 1 1.5 19.5V12a2.25 2.25 0 0 1 2.25-2.25h10.5v-3A5.25 5.25 0 0 1 18 1.5Z"/>
        </svg>
        Bearbeitung aktiv
    {:else}
        <!-- Lock icon -->
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-3.5 h-3.5">
            <path fill-rule="evenodd" d="M12 1.5a5.25 5.25 0 0 0-5.25 5.25v3a3 3 0 0 0-3 3V19.5a3 3 0 0 0 3 3h10.5a3 3 0 0 0 3-3v-6.75a3 3 0 0 0-3-3v-3A5.25 5.25 0 0 0 12 1.5Zm-1.5 8.25v-3a1.5 1.5 0 0 1 3 0v3h-3Z" clip-rule="evenodd"/>
        </svg>
        Nur Ansicht
    {/if}
</button>

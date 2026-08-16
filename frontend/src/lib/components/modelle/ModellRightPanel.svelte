<script lang="ts">
    export let description: string = '';
    export let formel: string = '';
    export let formeldesc: string = '';
    export let editable: boolean = true;

    // Für zwei-Wege-Bindung nach außen
    // Elternkomponente kann bind:description etc. nutzen
</script>

<div class="border-l p-3 pl-20 w-xl">
    <div class="mb-1">
        <label class="block text-gray-700 text-xs mb-1">Beschreibung – Modell</label>
        <textarea
            bind:value={description}
            name="description"
            disabled={!editable}
            class="w-full h-10 border border-gray-400 px-2 text-sm py-0 {editable ? 'bg-white' : 'bg-gray-50 cursor-not-allowed'}"
            rows="2"
        ></textarea>
    </div>
    <div class="mb-1">
        <label class="block text-gray-700 text-xs mb-1">Formel</label>
        <input
            type="text"
            bind:value={formel}
            name="formel"
            disabled={!editable}
            class="w-full h-6 border border-gray-400 px-2 text-sm py-0 {editable ? 'bg-white' : 'bg-gray-50 cursor-not-allowed'}"
        />
    </div>
    <div class="mb-1">
        <label class="block text-gray-700 text-xs mb-1">Beschreibung – Formel</label>
        <input
            type="text"
            bind:value={formeldesc}
            name="formeldesc"
            disabled={!editable}
            class="w-full h-6 border border-gray-400 px-2 text-sm py-0 {editable ? 'bg-white' : 'bg-gray-50 cursor-not-allowed'}"
        />
    </div>
</div>

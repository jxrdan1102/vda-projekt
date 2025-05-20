<script lang="ts">
    import type {ActionData, PageData} from './$types';

    export let data: PageData;
    export let form: ActionData;
</script>

<h1 class="text-2xl font-bold mb-4">Neue KMG hinzufügen</h1>

<form method="POST" class="space-y-4 max-w-md">
    <div>
        <label for="methode" class="block font-medium">Methode (iGeometrie_EN)</label>
        <input id="methode" name="methode" type="number" required class="w-full border rounded px-3 py-2" />
    </div>

    <div>
        <label for="name" class="block font-medium">Name</label>
        <input id="name" name="name" required class="w-full border rounded px-3 py-2" />
    </div>

    <div>
        <label for="aufgabe" class="block font-medium">Aufgabe (optional)</label>
        <input id="aufgabe" name="aufgabe" type="number" class="w-full border rounded px-3 py-2" />
    </div>

    <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        Speichern
    </button>
</form>

{#if form?.error}
    <p class="text-red-600 mt-4">{form.error}</p>
{:else if form?.message}
    <p class="text-green-600 mt-4">{form.message}</p>
{/if}

<script lang="ts">
    import type {ActionData, PageData} from './$types';

    export let data: PageData;
    export let form: ActionData;
    type Modell = {
        id: number;
        name: string; // oder ein anderer identifizierbarer Name
    };
</script>

<h1 class="text-2xl font-bold mb-4">Neues Analyseprojekt hinzufügen</h1>

<form method="POST" class="space-y-4 max-w-md">
    <div>
        <label for="modell" class="block font-medium">Modell</label>
        <select id="modell" name="modell" required class="w-full border rounded px-3 py-2">
            <option value="" disabled selected>Modell wählen</option>
            {#each data.models as modell}
                <option value={modell.id}>{modell.name} (ID: {modell.id})</option>
            {/each}
        </select>
    </div>

    <div>
        <label for="name" class="block font-medium">Name</label>
        <input id="name" name="name" required class="w-full border rounded px-3 py-2" />
    </div>

    <div>
        <label for="aenderungszustand" class="block font-medium">Änderungszustand (optional)</label>
        <input id="aenderungszustand" name="aenderungszustand" type="string" class="w-full border rounded px-3 py-2" />
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

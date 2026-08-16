<script lang="ts">
    import type {ActionData, PageData} from './$types';

    let aufgabe_modell = '';
    export let data: PageData;
    export let form: ActionData;
</script>

<h1 class="text-2xl font-bold mb-4">Neue KMG hinzufügen</h1>

<form method="POST" class="space-y-4 max-w-md">
    <div>
        <label for="aufgabe_modell" class="block font-medium">Prozess</label>
        <select
                id="aufgabe_modell"
                name="aufgabe_modell"
                bind:value={aufgabe_modell}
                required
                class="w-full border rounded px-3 py-2"
        >
            <option value="" disabled selected>Bitte wählen</option>
            <option value="1">Prüfprozess</option>
            <option value="2">Kalibrierprozess</option>
            <option value="3">3D-Prüfprozess</option>
        </select>
    </div>

    <div>
        <label for="name" class="block font-medium">Name</label>
        <input id="name" name="name" required class="w-full border rounded px-3 py-2" />
    </div>

    {#if aufgabe_modell === '3'}
        <div>
            <label for="aufgabe" class="block font-medium">Aufgabe</label>
            <select
                    id="aufgabe"
                    name="aufgabe"
                    required
                    class="w-full border rounded px-3 py-2"
            >
                <option value="" disabled selected>Bitte wählen</option>
                <option value="1">Durchmesser</option>
                <option value="2">Abstand</option>
                <option value="3">Richtung</option>
                <option value="4">Koaxialität</option>
                <option value="5">Form</option>
                <option value="6">Winkel</option>
                <option value="7">Position</option>
            </select>        </div>
    {/if}

    <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        Speichern
    </button>
</form>

{#if form?.error}
    <p class="text-red-600 mt-4">{form.error}</p>
{:else if form?.message}
    <p class="text-green-600 mt-4">{form.message}</p>
{/if}

<script lang="ts">
    export let data: { kmg: any };

    // Lokale reactive Variablen
    let name = data.kmg.name ?? '';
    let geo_me = data.kmg.geo_me ?? null;
    let geo_mo = data.kmg.geo_mo ?? null;
    let geo_bn = data.kmg.geo_bn ?? null;

    let tsk_ausenmessung = data.kmg.tsk_ausenmessung ?? 0;
    let tsk_innenmessung = data.kmg.tsk_innenmessung ?? 0;
    let tsk_tiefenmessung = data.kmg.tsk_tiefenmessung ?? 0;
    let tsk_hoehenmessung = data.kmg.tsk_hoehenmessung ?? 0;
    let tsk_stufenmessung = data.kmg.tsk_stufenmessung ?? 0;

    let formel = data.kmg.formel ?? '';
    let formeldesc = data.kmg.formeldesc ?? '';

    let message = '';
    let error = '';
</script>

<h1 class="text-2xl font-bold mb-4">Modell: {name}</h1>

<form method="POST" class="max-w-3xl space-y-6">
    <div>
        <label class="font-semibold block mb-1">Name</label>
        <input type="text" name="name" bind:value={name} class="w-full border rounded px-3 py-2" required />
    </div>

    <div class="grid grid-cols-3 gap-4">
        <div>
            <label class="font-semibold block mb-1">ME</label>
            <input type="number" name="geo_me" bind:value={geo_me} class="w-full border rounded px-3 py-2" />
        </div>
        <div>
            <label class="font-semibold block mb-1">MO</label>
            <input type="number" name="geo_mo" bind:value={geo_mo} class="w-full border rounded px-3 py-2" />
        </div>
        <div>
            <label class="font-semibold block mb-1">BN</label>
            <input type="number" name="geo_bn" bind:value={geo_bn} class="w-full border rounded px-3 py-2" />
        </div>
    </div>

    <fieldset class="border p-4 rounded space-y-2">
        <legend class="font-semibold mb-2">Messmethoden</legend>
        <label>
            <input type="checkbox" name="tsk_ausenmessung" bind:checked={tsk_ausenmessung} />
            Außenmessung
        </label><br />
        <label>
            <input type="checkbox" name="tsk_innenmessung" bind:checked={tsk_innenmessung} />
            Innenmessung
        </label><br />
        <label>
            <input type="checkbox" name="tsk_tiefenmessung" bind:checked={tsk_tiefenmessung} />
            Tiefenmessung
        </label><br />
        <label>
            <input type="checkbox" name="tsk_hoehenmessung" bind:checked={tsk_hoehenmessung} />
            Höhenmessung
        </label><br />
        <label>
            <input type="checkbox" name="tsk_stufenmessung" bind:checked={tsk_stufenmessung} />
            Stufenmessung
        </label>
    </fieldset>

    <div>
        <label class="font-semibold block mb-1">Formel</label>
        <textarea name="formel" bind:value={formel} rows="2" class="w-full border rounded px-3 py-2"></textarea>
    </div>

    <div>
        <label class="font-semibold block mb-1">Formel Beschreibung</label>
        <textarea name="formeldesc" bind:value={formeldesc} rows="2" class="w-full border rounded px-3 py-2"></textarea>
    </div>

    <button type="submit" class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
        Speichern
    </button>

    {#if message}
        <p class="text-green-600 mt-3">{message}</p>
    {/if}
    {#if error}
        <p class="text-red-600 mt-3">{error}</p>
    {/if}
</form>

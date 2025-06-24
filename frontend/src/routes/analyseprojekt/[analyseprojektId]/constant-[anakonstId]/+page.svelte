<script lang="ts">
    import {tcMapping} from "$lib/Mapping";

    export let data: { constant: any };

    const constant = data.constant;

    let constval: number = constant.constval ?? 0;

    function cancel() {
        history.back();
    }
</script>
<form method="POST" class="mx-auto rounded bg-white">
    <h2 class="text-l font-bold text-black-800 mb-1">{tcMapping[constant.constnum]}</h2>

    <input type="number" name="constval" bind:value={constval} step="any" class="w-full border rounded px-2 py-1" />

    <button type="submit" class="bg-gray-800 text-white px-3 py-1 rounded hover:bg-gray-900 mt-2">
        Speichern
    </button>
</form>

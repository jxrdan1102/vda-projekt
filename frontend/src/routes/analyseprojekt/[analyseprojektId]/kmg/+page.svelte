<script lang="ts">

    export let data: { kmg: any };

    const kmg = data.kmg;

</script>
<form method="POST" class="mx-auto rounded bg-white">
    <h2 class="text-l font-bold text-black-800 mb-1">KMGs</h2>
    {#each kmg as kmg}
        <div class="flex gap-5">
            <div>{kmg.id}</div>
            <div>{kmg.kmg_bez}</div>
        </div>
    {/each}

        <button type="submit" class="bg-gray-800 text-white px-3 py-1 rounded hover:bg-gray-900 mt-2">
        Speichern
    </button>
</form>

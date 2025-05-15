<script lang="ts">
    let { data } = $props();
    $inspect(data);
</script>
<h1> HELLO </h1>
<h1>{data.title}</h1>
<p>{JSON.stringify(data.kmg, null, 2)}</p>
<a href="/kmgs/5" data-sveltekit-preload-data="hover"> Hier geht's weiter</a>
<a href="/kmgs/6" data-sveltekit-preload-data="hover"> Hier sogar auch </a>
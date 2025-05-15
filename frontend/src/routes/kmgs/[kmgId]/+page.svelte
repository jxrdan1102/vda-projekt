<script lang="ts">
    let { data } = $props();
    $inspect(data);
</script>
<h1> HELLO </h1>
<h1>{data.title}</h1>
<p>{JSON.stringify(data.kmg, null, 2)}</p>
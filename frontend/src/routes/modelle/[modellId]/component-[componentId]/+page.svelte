<script lang="ts">
  import ComponentEditForm from '$lib/components/modelle/ComponentEditForm.svelte';
  export let data;
</script>

<ComponentEditForm mode="standard" {data} />
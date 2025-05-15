<script lang="ts">
    import '../app.css';
    // State
    let value = $state('files');
    let { children } = $props();
</script>

{@render children()}

<script lang="ts">
    import '../app.css';
    // State
    let value = $state('files');
    let { children } = $props();
</script>

<nav class="bg-blue-800 text-white px-6 py-4 shadow-md">
    <div class="max-w-7xl mx-auto flex justify-between items-center">
        <div class="text-2xl font-semibold tracking-wide">Kister Metrologie</div>
        <ul class="flex space-x-6 text-sm font-medium">
            <li>
                <a href="/" class="hover:text-blue-200 transition">Dashboard</a>
            </li>
            <li>
                <a href="/admin" class="hover:text-blue-200 transition">Admin</a>
            </li>
            <li>
                <a href="/kmgs" class="hover:text-blue-200 transition">Modelle</a>
            </li>
        </ul>
    </div>
</nav>

<main class="bg-gray-50 min-h-screen p-6">
    {@render children()}
</main>
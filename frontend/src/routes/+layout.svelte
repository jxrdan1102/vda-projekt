<script lang="ts">
    import '../app.css';
    // State
    let value = $state('files');
    let { children } = $props();
</script>

<nav class="bg-green-600 text-black px-6 py-4 shadow-md">
    <div class="max-w-8xl mx-auto flex justify-between items-center text-white">
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
            <li>
                <a href="/analyseprojekt" class="hover:text-blue-200 transition">Analyseprojekte</a>
            </li>
        </ul>
    </div>
</nav>

<main class="bg-gray-50 min-h-screen px-6 pb-6">
    {@render children()}
</main>
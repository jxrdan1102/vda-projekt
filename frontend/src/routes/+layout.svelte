<script lang="ts">
    import '../app.css';
    let value = $state('files');
    let { children } = $props();
</script>

<nav class="text-white px-6 py-4 shadow-md" style="background-color: #1f3b5e;">
    <div class="max-w-8xl mx-auto flex justify-between items-center">
        <div class="text-2xl font-semibold tracking-wide">Kistner Metrologie</div>
        <ul class="flex space-x-6 text-sm font-medium">
            <li>
                <a href="/dashboard" class="hover:text-blue-300 transition">Dashboard</a>
            </li>
            <li>
                <a href="/admin" class="hover:text-blue-300 transition">Admin</a>
            </li>
            <li>
                <a href="/modelle" class="hover:text-blue-300 transition">Modelle</a>
            </li>
            <li>
                <a href="/analyseprojekt" class="hover:text-blue-300 transition">Analyseprojekte</a>
            </li>
        </ul>
    </div>
</nav>
<main class="min-h-screen px-6 pb-6" style="background-color: #f0f0f0;">
    {@render children()}
</main>
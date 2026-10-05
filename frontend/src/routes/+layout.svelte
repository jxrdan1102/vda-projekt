<script lang="ts">
    import '../app.css';
    import { page } from '$app/state';
    import { ROLE_LABELS, isAdminRole } from '$lib/roles';

    let { children, data } = $props();

    let menuOpen = $state(false);
    const isAdmin = $derived(isAdminRole(data.user?.role));

    // Menü bei Seitenwechsel schließen
    $effect(() => {
        page.url.pathname;
        menuOpen = false;
    });

    function closeOnOutside(node: HTMLElement) {
        const handler = (e: MouseEvent) => {
            if (!node.contains(e.target as Node)) menuOpen = false;
        };
        document.addEventListener('click', handler);
        return { destroy: () => document.removeEventListener('click', handler) };
    }
</script>

<nav class="text-white px-6 py-4 shadow-md" style="background-color: #1f3b5e;">
    <div class="max-w-8xl mx-auto flex justify-between items-center">
        <div class="text-2xl font-semibold tracking-wide">Kistner Metrologie</div>
        {#if data.user}
            <ul class="flex space-x-6 text-sm font-medium items-center">
                <li><a href="/dashboard" class="hover:text-blue-300 transition">Dashboard</a></li>
                <li><a href="/modelle" class="hover:text-blue-300 transition">Modelle</a></li>
                <li><a href="/analyseprojekt" class="hover:text-blue-300 transition">Analyseprojekte</a></li>
                {#if isAdmin}
                    <li><a href="/admin" class="hover:text-blue-300 transition">Verwaltung</a></li>
                {/if}

                <!-- Benutzer-Menü -->
                <li class="relative border-l border-white/30 pl-6" use:closeOnOutside>
                    <button
                        class="flex items-center gap-2 hover:text-blue-300 transition"
                        aria-haspopup="menu"
                        aria-expanded={menuOpen}
                        onclick={() => (menuOpen = !menuOpen)}
                    >
                        {data.user.sub}
                        <span class="rounded px-1.5 py-0.5 text-xs {data.user.role === 'superadmin' ? 'bg-amber-500 text-black' : 'bg-white/20'}">
                            {ROLE_LABELS[data.user.role] ?? data.user.role}
                        </span>
                        <span aria-hidden="true">▾</span>
                    </button>

                    {#if menuOpen}
                        <div role="menu" class="absolute right-0 mt-2 w-56 rounded border bg-white py-1 text-gray-800 shadow-lg z-50">
                            <a role="menuitem" href="/konto" class="block px-4 py-2 hover:bg-gray-100">Mein Konto</a>
                            {#if isAdmin}
                                <div class="my-1 border-t"></div>
                                <div class="px-4 pt-1 pb-0.5 text-xs font-semibold uppercase text-gray-400">Verwaltung</div>
                                <a role="menuitem" href="/admin" class="block px-4 py-2 hover:bg-gray-100">Übersicht</a>
                                {#if data.user.role === 'superadmin'}
                                    <a role="menuitem" href="/admin/firmen" class="block px-4 py-2 hover:bg-gray-100">Firmen</a>
                                {/if}
                                <a role="menuitem" href="/admin/nutzer" class="block px-4 py-2 hover:bg-gray-100">Nutzer</a>
                            {/if}
                            <div class="my-1 border-t"></div>
                            <form method="POST" action="/logout">
                                <button role="menuitem" type="submit" class="w-full text-left px-4 py-2 hover:bg-gray-100 text-red-700">Abmelden</button>
                            </form>
                        </div>
                    {/if}
                </li>
            </ul>
        {/if}
    </div>
</nav>
<main class="min-h-screen px-6 pb-6" style="background-color: #f0f0f0;">
    {@render children()}
</main>

<script lang="ts">
    import '../app.css';
    import { page, navigating } from '$app/state';
    import { ROLE_LABELS, isAdminRole } from '$lib/roles';
    import Notifications from '$lib/components/Notifications.svelte';

    let { children, data } = $props();

    let menuOpen = $state(false);
    const isAdmin = $derived(isAdminRole(data.user?.role));
    const canWrite = $derived(data.user && data.user.role !== 'readonly');

    const APP_NAME = 'Kistner Metrologie';

    // Titel im Browser-Tab, z. B. "Analyseprojekt – Welle 3 · Kistner Metrologie"
    function pageLabel(r: string): string {
        if (r.startsWith('/admin/firmen')) return 'Firmen';
        if (r.startsWith('/admin/nutzer')) return 'Nutzer';
        if (r.startsWith('/admin')) return 'Verwaltung';
        if (r.startsWith('/konto')) return 'Mein Konto';
        if (r.startsWith('/login')) return 'Anmelden';
        if (r.startsWith('/import')) return 'Import';
        if (r.startsWith('/dashboard')) return 'Übersicht';
        if (r.endsWith('/MU')) return 'Messunsicherheit';
        if (r.endsWith('/kmg')) return 'KMG';
        if (r.includes('/component-')) return 'Komponente';
        if (r.includes('/constant-')) return 'Konstante';
        if (r.endsWith('/addComponent')) return 'Komponente hinzufügen';
        if (r === '/modelle/add') return 'Neues Modell';
        if (r === '/analyseprojekt/add') return 'Neues Analyseprojekt';
        if (r.startsWith('/modelle/')) return 'Modell';
        if (r.startsWith('/modelle')) return 'Modelle';
        if (r.startsWith('/analyseprojekt/')) return 'Analyseprojekt';
        if (r.startsWith('/analyseprojekt')) return 'Analyseprojekte';
        return '';
    }
    const pageTitle = $derived.by(() => {
        const label = pageLabel(page.route.id ?? '');
        const d = page.data as Record<string, any>;
        const name = d?.analyseprojekt?.name ?? d?.modell?.name;
        const main = [label, name].filter(Boolean).join(' – ');
        return main ? `${main} · ${APP_NAME}` : APP_NAME;
    });

    // Ladeanzeige: nur wenn ein Seitenwechsel länger als 300 ms dauert (z. B. Berechnung)
    let showLoading = $state(false);
    $effect(() => {
        if (!navigating.to) {
            showLoading = false;
            return;
        }
        const t = setTimeout(() => (showLoading = true), 300);
        return () => clearTimeout(t);
    });
    const loadingText = $derived(
        navigating.to?.route.id?.endsWith('/MU') ? 'Messunsicherheit wird berechnet …' : 'Wird geladen …'
    );

    // "← Zurück"-Link auf Unterseiten von Modellen und Analyseprojekten
    const backLink = $derived.by(() => {
        if (page.status >= 400) return null; // Fehlerseite hat eigene Knöpfe
        const parts = page.url.pathname.split('/').filter(Boolean);
        if (parts.length < 2 || !['modelle', 'analyseprojekt'].includes(parts[0])) return null;
        const href = '/' + parts.slice(0, -1).join('/');
        if (parts.length === 2) {
            return parts[0] === 'modelle'
                ? { href, label: 'Zurück zu den Modellen' }
                : { href, label: 'Zurück zu den Analyseprojekten' };
        }
        return parts[0] === 'modelle'
            ? { href, label: 'Zurück zum Modell' }
            : { href, label: 'Zurück zum Analyseprojekt' };
    });

    // aktiven Menüpunkt hervorheben
    const navClass = (href: string) =>
        page.url.pathname.startsWith(href)
            ? 'text-white border-b-2 border-blue-300 pb-0.5'
            : 'text-white/90 hover:text-blue-300 transition';

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

<svelte:head>
    <title>{pageTitle}</title>
</svelte:head>

<Notifications />

{#if showLoading}
    <div class="fixed top-0 left-0 right-0 z-[80] h-1 overflow-hidden bg-blue-100" role="progressbar" aria-label={loadingText}>
        <div class="h-full w-1/3 bg-blue-500 loading-bar"></div>
    </div>
    <div class="fixed bottom-4 left-1/2 -translate-x-1/2 z-[80] flex items-center gap-2 rounded-full bg-[#1f3b5e] px-4 py-2 text-sm text-white shadow-lg">
        <span class="inline-block w-3 h-3 border-2 border-white/40 border-t-white rounded-full animate-spin" aria-hidden="true"></span>
        {loadingText}
    </div>
{/if}

<nav class="text-white px-6 py-4 shadow-md" style="background-color: #1f3b5e;">
    <div class="max-w-8xl mx-auto flex justify-between items-center">
        <a href="/dashboard" class="text-2xl font-semibold tracking-wide">Kistner Metrologie</a>
        {#if data.user}
            <ul class="flex space-x-6 text-sm font-medium items-center">
                <li><a href="/dashboard" class={navClass('/dashboard')}>Übersicht</a></li>
                <li><a href="/modelle" class={navClass('/modelle')}>Modelle</a></li>
                <li><a href="/analyseprojekt" class={navClass('/analyseprojekt')}>Analyseprojekte</a></li>
                {#if canWrite}
                    <li><a href="/import" class={navClass('/import')}>Import</a></li>
                {/if}
                {#if isAdmin}
                    <li><a href="/admin" class={navClass('/admin')}>Verwaltung</a></li>
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
    {#if backLink}
        <div class="pt-3 -mb-1">
            <a href={backLink.href} class="inline-flex items-center gap-1 text-sm text-[#1f3b5e] hover:underline">
                <span aria-hidden="true">←</span> {backLink.label}
            </a>
        </div>
    {/if}
    {@render children()}
</main>

<style>
    .loading-bar {
        animation: loading-slide 1.1s ease-in-out infinite;
    }
    @keyframes loading-slide {
        from { transform: translateX(-100%); }
        to { transform: translateX(300%); }
    }
</style>

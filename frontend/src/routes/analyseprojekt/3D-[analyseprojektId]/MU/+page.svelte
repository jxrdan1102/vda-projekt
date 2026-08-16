<script>
    import {onMount} from "svelte";
    import Chart from "chart.js/auto";
    import ChartDataLabels from "chartjs-plugin-datalabels";
    import { COMPONENTS, Components } from '$lib/Mapping';
    
    export let data;
    let analyseprojekt = data.analyseprojekt;
    let messunsicherheit = data.messunsicherheit;
    let canvas;

    const COMPONENT_IDS = Object.fromEntries(
    Object.entries(COMPONENTS).map(([id, value]) => [value, Number(id)])
    );

    // Sortierte Komponenten nach Unsicherheitsbeitrag
    let komponenten = [...messunsicherheit.Komponenten]
        .sort((a, b) => (b[1] ?? 0) - (a[1] ?? 0));
    function roundHalfUp(value, decimals = 2) {
        const factor = 10 ** decimals;
        return Math.round((value + Number.EPSILON) * factor) / factor;
    }

    onMount(() => {
        new Chart(canvas, {
            type: "bar",
            data: {
                labels: komponenten.map(([klasse]) =>
                Components[COMPONENT_IDS[klasse]] ?? klasse
                ),
                datasets: [
                    {
                        label: "Unsicherheitsbeitrag",
                        data: komponenten.map(([_, ub]) => ub ?? 0),
                        backgroundColor: "#6366F1", // Indigo-500
                        borderRadius: 4,
                        barThickness: 24
                    }
                ]
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    datalabels: {
                        anchor: "end",
                        align: "right",
                        formatter: (val) => roundHalfUp(val, 3).toFixed(3),
                        font: {
                            size: 11,
                            weight: "bold"
                        },
                        color: "#111"
                    }
                },
                layout: {
                    padding: 10
                },
                scales: {
                    x: {
                        ticks: {
                            font: { size: 10 }
                        },
                        grid: { display: false }
                    },
                    y: {
                        ticks: {
                            font: { size: 10 }
                        },
                        grid: { display: false }
                    }
                }
            },
            plugins: [ChartDataLabels]
        });
    });
</script>

<!-- Abschnitt: Zusammenfassung -->
<h2 class="text-lg font-semibold mb-2">Messunsicherheit – Übersicht</h2>

<div class="bg-indigo-50 rounded-lg p-5 border border-indigo-200 shadow-sm mt-6 text-gray-800 text-sm font-medium max-w-2xl mx-auto">
    <div class="flex flex-col sm:flex-row sm:space-x-8 space-y-3 sm:space-y-0">
        <div class="flex flex-col">
            <span class="text-indigo-700 font-semibold mb-1">Projektname</span>
            <span class="text-indigo-900 truncate">{analyseprojekt.name}</span>
        </div>
        <div class="flex flex-col border-t border-indigo-200 pt-3 sm:pt-0 sm:border-t-0 sm:border-l sm:pl-8">
            <span class="text-indigo-700 font-semibold mb-1">Änderungsstand</span>
            <span>{analyseprojekt.aenderungszustand}</span>
        </div>
        <div class="flex flex-col border-t border-indigo-200 pt-3 sm:pt-0 sm:border-t-0 sm:border-l sm:pl-8">
            <span class="text-indigo-700 font-semibold mb-1">Modell</span>
            <span>{analyseprojekt.modell.name}</span>
        </div>
    </div>
</div>

<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6 max-w-2xl mx-auto">
    <div class="bg-white rounded-lg p-3 border shadow-sm">
        <p class="text-gray-500 text-xs">Erweiterte Messunsicherheit (µm)</p>
        <p class="text-indigo-600 font-semibold text-lg">
            {messunsicherheit.Unsicherheit.toFixed(3)}
        </p>
    </div>
    <div class="bg-white rounded-lg p-3 border shadow-sm">
        <p class="text-gray-500 text-xs">Erweiterungsfaktor k</p>
        <p class="text-indigo-600 font-semibold text-lg">
            {messunsicherheit.Erweiterungsfaktor.toFixed(3)}
        </p>
    </div>
</div>

<!-- Abschnitt: Komponenten als Diagramm -->
<div class="w-full h-[320px] max-w-4xl mx-auto mt-8" style="text-align: center;">
Unsicherheitsbeiträge (µm)
    <canvas bind:this={canvas}></canvas>
</div>

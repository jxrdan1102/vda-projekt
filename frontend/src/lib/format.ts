/* ── Zahlen deutsch formatieren (Komma statt Punkt) ── */

/** Kaufmännisch runden (2,0005 → 2,001), ohne Gleitkomma-Ausreißer. */
export function roundHalfUp(value: number, decimals = 3): number {
    const factor = 10 ** decimals;
    return Math.round((value + Number.EPSILON) * factor) / factor;
}

/** Zahl mit fester Anzahl Nachkommastellen, z. B. 1,234 */
export function zahl(value: number | null | undefined, decimals = 3): string {
    if (value === null || value === undefined || Number.isNaN(value)) return '–';
    return roundHalfUp(value, decimals).toLocaleString('de-DE', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

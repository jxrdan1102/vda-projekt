// src/lib/components/analyseprojekt/types.ts
//
// Typen für die generische KomponentenTabelle.
// Beide Seiten (Standard + 3D) beschreiben ihre Spalten mit diesem Interface.

// ---------------------------------------------------------------
// Ein einzelnes Feld das in einer Tabellenzelle editierbar ist
// ---------------------------------------------------------------

export type FieldType =
    | 'number'   // <input type="number">
    | 'select'   // <select>
    | 'checkbox' // <input type="checkbox">
    | 'text' // <input type="text">

export interface SelectOption {
    value: number | string;
    label: string;
}

export interface ColumnDef {
    /** Interner Feldname auf dem comp-Objekt, z.B. 'terml0' */
    field: string;

    /** Spaltenüberschrift */
    header: string;

    /** Wie wird der Wert im Nur-Lese-Modus dargestellt? */
    display?: (comp: any) => string;

    /** Feldtyp für den Edit-Modus */
    type: FieldType;

    /** Nur für type='select': die Optionen */
    options?: SelectOption[];

    /**
     * Optionale Bedingung, wann die Zelle editierbar ist.
     * Standard: immer editierbar.
     * Beispiel 3D: 'anzahl_messungen' nur wenn comp.wertart === 4
     */
    editableWhen?: (comp: any) => boolean;

    /**
     * Nur für 3D: Checkbox "berechnen" neben dem Wert anzeigen,
     * wenn comp.wertart === 5
     */
    showBerechnenCheckbox?: boolean;
}

// ---------------------------------------------------------------
// Vordefinierte Spaltensätze für die beiden Varianten
// ---------------------------------------------------------------

/** Standard-Analyseprojekt (terml0, terml1, verteilung, wertart, freigrad) */
export const STANDARD_COLUMNS: ColumnDef[] = [
    {
        field: 'terml0',
        header: 'L0 längenunabhängiger Term',
        type: 'text',
    },
    {
        field: 'terml1',
        header: 'L1 längenabhängiger Term',
        type: 'text',
    },
    {
        field: 'verteilung',
        header: 'Verteilung',
        type: 'select',
        options: [
            { value: 1, label: 'Rechteckverteilung' },
            { value: 2, label: 'Normalverteilung' },
            { value: 3, label: 'Dreieckverteilung' },
        ],
        display: (comp) => {
            const map: Record<number, string> = {
                1: 'Rechteckverteilung',
                2: 'Normalverteilung',
                3: 'Dreieckverteilung',
            };
            return map[comp.verteilung] ?? String(comp.verteilung ?? '');
        },
    },
    {
        field: 'wertart',
        header: 'Streuungsparameter',
        type: 'select',
        options: [
            { value: 1, label: 'Halbweite' },
            { value: 2, label: 'Spannweite' },
            { value: 3, label: 'Standardabweichung' },
        ],
        display: (comp) => {
            const map: Record<number, string> = {
                1: 'Halbweite',
                2: 'Spannweite',
                3: 'Standardabweichung',
            };
            return map[comp.wertart] ?? String(comp.wertart ?? '');
        },
    },
    {
        field: 'freigrad',
        header: 'Freiheitsgrad',
        type: 'select',
        options: [
            { value: 1, label: 'Unbegrenzt' },
            { value: 2, label: 'N-1' },
        ],
        display: (comp) => {
            const map: Record<number, string> = {
                1: 'Unbegrenzt',
                2: 'N-1',
            };
            return map[comp.freigrad] ?? String(comp.freigrad ?? '');
        },
    },
];

/** 3D-Analyseprojekt (terml0/Standardabw., wertart/Methode, messpunkt_anzahl, anzahl_messungen) */
export const DREID_COLUMNS: ColumnDef[] = [
    {
        field: 'berechnen',
        header: 'A/3',
        type: 'checkbox',
        showBerechnenCheckbox: true,
    },
    {
        field: 'terml0',
        header: 'Standardabweichung',
        type: 'text',
        showBerechnenCheckbox: true,
    },
    {
        field: 'wertart',
        header: 'Methode',
        type: 'select',
        options: [
            { value: 4, label: 'A' },
            { value: 5, label: 'B' },
        ],
    },
    {
        field: 'messpunkt_anzahl',
        header: 'Anzahl Messpunkte',
        type: 'number',
    },
    {
        field: 'anzahl_messungen',
        header: 'Anzahl Messungen',
        type: 'number',
    },
];

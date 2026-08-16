// Geteilte Konstanten für Komponenten-Formulare

export const MODLTXT_OPTIONS = [
    { value: 0, label: 'Bitte wählen' },
    { value: 1, label: 'Das ist eine tolle Komponente' },
    { value: 2, label: 'Diese Komponente ist sehr nützlich' },
] as const;

export const PROZESSTITEL: Record<number, string> = {
    1: 'Prüfprozess',
    2: 'Kalibrierprozess',
    3: '3D-Prüfprozess',
};

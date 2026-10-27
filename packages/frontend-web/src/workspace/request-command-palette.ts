/**
 * Gleicher Einstieg wie AppShell Strg+K.
 * Oeffnet die bereits gemountete Palette, keine zweite Kommandozeile.
 */
export function requestExistingCommandPalette(): void {
  window.dispatchEvent(
    new KeyboardEvent('keydown', {
      key: 'k',
      code: 'KeyK',
      ctrlKey: true,
      bubbles: true,
      cancelable: true,
    }),
  )
}

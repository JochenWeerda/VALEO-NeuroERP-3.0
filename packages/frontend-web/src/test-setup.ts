import "@testing-library/jest-dom/vitest";

// Unconditional matchMedia stub — JSDOM does not implement it at all.
// Overwrite even if partially defined so useTouchDevice() always gets a safe implementation.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
(window as any).matchMedia = ((query: string) => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: () => {},
  removeListener: () => {},
  addEventListener: () => {},
  removeEventListener: () => {},
  dispatchEvent: () => false,
})) as Window["matchMedia"];

// Polyfill ResizeObserver if not present (JSDOM < v20).
if (!("ResizeObserver" in window)) {
  class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  }
  // @ts-expect-error - polyfill assignment
  window.ResizeObserver = ResizeObserver;
}

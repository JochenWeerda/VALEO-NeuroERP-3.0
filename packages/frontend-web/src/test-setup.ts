import "@testing-library/jest-dom/vitest";

// Optional shims for JSDOM gaps that surface in component tests.
if (!("matchMedia" in window)) {
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
}

// Polyfill ResizeObserver if not present (JSDOM < v20).
if (!("ResizeObserver" in window)) {
  class ResizeObserver {
    /* eslint-disable @typescript-eslint/no-empty-function */
    observe() {}
    unobserve() {}
    disconnect() {}
    /* eslint-enable @typescript-eslint/no-empty-function */
  }
  // @ts-expect-error - polyfill assignment
  window.ResizeObserver = ResizeObserver;
}

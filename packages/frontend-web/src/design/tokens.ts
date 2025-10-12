import tokens from "../../specs/tokens.spec.json";

type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends Record<string, unknown>
    ? DeepReadonly<T[K]>
    : T[K];
};

export type DesignTokens = DeepReadonly<typeof tokens>;

/**
 * Canonical design tokens for VALEO NeuroERP.
 * Use this helper to access token values instead of hardcoding colors,
 * spacing or typography in components.
 */
export const designTokens: DesignTokens = tokens;

type PathSegments = string | number;

/**
 * Utility to resolve a token using dot-separated path notation.
 * Example: getToken("colors.brand.primary.500")
 */
export function getToken(path: string): unknown {
  const segments = path.split(".").filter(Boolean) as PathSegments[];
  return segments.reduce<unknown>((acc, segment) => {
    if (acc && typeof acc === "object" && segment in acc) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return (acc as Record<PathSegments, unknown>)[segment];
    }
    throw new Error(`Design token "${path}" not found.`);
  }, designTokens);
}

/**
 * Convenience helper for color tokens. Returns the HEX string for the
 * requested token (e.g. `brand.primary.500`).
 */
export function getColorToken(path: string): string {
  const value = getToken(`colors.${path}`);
  if (typeof value !== "string") {
    throw new Error(`Design token colors.${path} is not a string.`);
  }
  return value;
}


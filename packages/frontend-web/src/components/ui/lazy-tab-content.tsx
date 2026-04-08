import { type ReactNode, useState, useEffect } from "react";

interface LazyTabContentProps {
  active: boolean;
  children: ReactNode;
  /** Keep content mounted after first activation (default: true) */
  keepMounted?: boolean;
}

/**
 * Only renders children when the tab becomes active.
 * Once activated, keeps content in DOM to avoid re-fetching (unless keepMounted=false).
 */
export function LazyTabContent({ active, children, keepMounted = true }: LazyTabContentProps) {
  const [hasBeenActive, setHasBeenActive] = useState(false);

  useEffect(() => {
    if (active && !hasBeenActive) {
      setHasBeenActive(true);
    }
  }, [active, hasBeenActive]);

  const shouldRender = keepMounted ? hasBeenActive : active;

  if (!shouldRender) return null;

  return <div style={{ display: active ? undefined : "none" }}>{children}</div>;
}

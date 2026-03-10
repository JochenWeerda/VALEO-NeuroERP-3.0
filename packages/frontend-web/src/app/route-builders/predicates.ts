const AUTO_ROUTE_IGNORE_PATTERNS: RegExp[] = [
  /\/__tests__\//,
  /\.spec\.tsx$/,
  /\.test\.tsx$/,
  /\.stories\.tsx$/,
  /\/finance\/reports\/[^/]+\.tsx$/,
  /\/charts\//,
  /\/Dlg[A-Z][^/]*\.tsx$/,
]

export function isPortalModule(modulePath: string): boolean {
  return modulePath.includes('/portal/')
}

export function isProspectingModule(moduleSpecifier: string): boolean {
  return moduleSpecifier.includes('/prospecting/')
}

export function isAutoRoutable(modulePath: string, prospectingEnabled: boolean): boolean {
  if (!prospectingEnabled && isProspectingModule(modulePath)) {
    return false
  }

  return !AUTO_ROUTE_IGNORE_PATTERNS.some((pattern) => pattern.test(modulePath))
}

export function isAutoRoutableMainApp(modulePath: string, prospectingEnabled: boolean): boolean {
  if (isPortalModule(modulePath)) {
    return false
  }

  return isAutoRoutable(modulePath, prospectingEnabled)
}

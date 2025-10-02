export interface PathAlias {
    alias: string;
    target: string;
}
export declare class PathResolver {
    private readonly aliases;
    constructor(initialAliases?: PathAlias[]);
    registerAlias(alias: string, target: string): void;
    hasAlias(alias: string): boolean;
    resolve(importPath: string, fromPath?: string): string;
    clear(): void;
    private findAlias;
    private normalize;
}
export declare const defaultPathResolver: PathResolver;
//***REMOVED*** sourceMappingURL=path-resolver.d.ts.map
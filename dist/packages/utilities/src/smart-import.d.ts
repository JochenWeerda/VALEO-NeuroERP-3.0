import { ModuleFederationService } from './module-federation-service';
export declare class SmartImport {
    private readonly federation;
    constructor(federation?: ModuleFederationService);
    dynamic<TModule>(importer: () => Promise<TModule>): Promise<TModule extends {
        default: infer TResult;
    } ? TResult : TModule>;
    remote<TModule = unknown>(moduleName: string): Promise<TModule>;
    resolve(moduleId: string, fromPath?: string): string;
}
export declare const smartImport: SmartImport;
//***REMOVED*** sourceMappingURL=smart-import.d.ts.map
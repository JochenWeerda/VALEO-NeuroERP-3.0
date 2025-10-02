import { moduleFederationService } from './module-federation-service';
export class SmartImport {
    federation;
    constructor(federation = moduleFederationService) {
        this.federation = federation;
    }
    async dynamic(importer) {
        const moduleInstance = await importer();
        if (moduleInstance && typeof moduleInstance === 'object' && 'default' in moduleInstance) {
            return (moduleInstance.default ?? moduleInstance);
        }
        return moduleInstance;
    }
    async remote(moduleName) {
        return this.federation.importRemoteModule(moduleName);
    }
    resolve(moduleId, fromPath) {
        return this.federation.resolveModulePath(moduleId, fromPath);
    }
}
export const smartImport = new SmartImport();

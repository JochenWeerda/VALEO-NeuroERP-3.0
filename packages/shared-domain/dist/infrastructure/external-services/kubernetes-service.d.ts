/**
 * Kubernetes Service - MSOA Implementation nach Clean Architecture
 * Infrastructure Layer Service migrated to VALEO-NeuroERP-3.0
 * External orchestration and container management
 */
import { Brand } from '@valero-neuroerp/data-models/src/branded-types';
export type DeploymentId = Brand<string, 'DeploymentId'>;
export type ServiceNamespace = Brand<string, 'ServiceNamespace'>;
export type PodId = Brand<string, 'PodId'>;
export interface KubernetesDeployment {
    readonly id: DeploymentId;
    readonly name: string;
    readonly namespace: ServiceNamespace;
    readonly image: string;
    readonly replicas: number;
    readonly resources: ResourceRequirements;
    readonly healthChecks: HealthCheckConfig[];
    readonly environment: EnvironmentConfig[];
    readonly status: 'DEPLOYING' | 'RUNNING' | 'STOPPED' | 'ERROR';
}
export interface ResourceRequirements {
    readonly requests: {
        readonly cpu: string;
        readonly memory: string;
    };
    readonly limits: {
        readonly cpu: string;
        readonly memory: string;
    };
}
export interface HealthCheckConfig {
    readonly type: 'HTTP' | 'TCP' | 'COMMAND';
    readonly path?: string;
    readonly port?: number;
    readonly command?: string[];
    readonly initialDelaySeconds: number;
    readonly periodSeconds: number;
    readonly timeoutSeconds: number;
    readonly failureThreshold: number;
}
export interface EnvironmentConfig {
    readonly name: string;
    readonly value?: string;
    readonly configMapRef?: string;
    readonly secretRef?: string;
}
export interface KubernetesService {
    readonly name: string;
    readonly type: 'ClusterIP' | 'NodePort' | 'LoadBalancer';
    readonly targetPort: number;
    readonly port: number;
    readonly selector: Record<string, string>;
}
export interface ConfigMap {
    readonly name: string;
    readonly namespace: ServiceNamespace;
    readonly data: Record<string, string>;
    readonly annotations: Record<string, string>;
}
export interface ClusterHealthStatus {
    readonly overallStatus: 'HEALTHY' | 'DEGRADED' | 'UNHEALTHY';
    readonly deploymentCount: number;
    readonly runningDeployments: number;
    readonly coverage: number;
}
export declare class KubernetesService {
    private readonly deployments;
    private readonly services;
    private readonly configMaps;
    private readonly clusterConfig;
    constructor();
    /**
     * Initialize Kubernetes Service
     */
    private initializeKubernetesService;
    /**
     * Setup Default Deployments nach Infrastructure Architecture
     */
    private setupDefaultDeployments;
    /**
     * Create Core Services Deployment
     */
    private createCoreServicesDeployment;
    /**
     * Create Database Deployment
     */
    private createDatabaseDeployment;
    /**
     * Create API Gateway Deployment
     */
    private createAPIProxyDeployment;
    /**
     * Create Observability Deployment
     */
    private createObservabilityDeployment;
    /**
     * Deploy Service
     */
    deployService(serviceConfig: {
        name: string;
        image: string;
        namespace: string;
        replicas?: number;
        resources?: ResourceRequirements;
        healthChecks?: HealthCheckConfig[];
        environment?: EnvironmentConfig[];
    }): Promise<DeploymentId>;
    /**
     * Get Cluster Health
     */
    getClusterHealth(): Promise<ClusterHealthStatus>;
    /**
     * Health check
     */
    healthCheck(): Promise<boolean>;
    private generateDeploymentId;
}
/**
 * Register Kubernetes Service in DI Container
 */
export declare function registerKubernetesService(): void;
//# sourceMappingURL=kubernetes-service.d.ts.map
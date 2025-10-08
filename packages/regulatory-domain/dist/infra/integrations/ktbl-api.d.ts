export interface KTBLEmissionCategory {
    direct: number;
    indirect: number;
    upstream: number;
    total: number;
}
export interface KTBLCropParameters {
    crop: string;
    region?: string;
    yieldPerHa: number;
    nitrogenFertilizer: number;
    emissions: KTBLEmissionCategory;
    source: string;
    calculatedAt: string;
}
export declare function fetchKTBLEmissionParameters(crop: string, region?: string): Promise<KTBLCropParameters | null>;
export declare function calculateCropEmissions(crop: string, options?: {
    yieldPerHa?: number;
    fertilizer?: number;
    region?: string;
}): Promise<{
    emissionsPerTon: number;
    breakdown: KTBLEmissionCategory;
    dataSource: string;
}>;
export declare function getKTBLStatus(): Promise<{
    available: boolean;
    lastCheck: string;
    message: string;
    fallbackActive: boolean;
}>;
export declare function getCachedKTBLData(crop: string, region?: string): KTBLCropParameters | null;
export declare function setCachedKTBLData(crop: string, region: string | undefined, data: KTBLCropParameters): void;
//# sourceMappingURL=ktbl-api.d.ts.map
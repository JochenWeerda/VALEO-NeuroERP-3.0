import { JWTPayload } from 'jose';
export declare function verifyJWT(token: string): Promise<JWTPayload>;
export declare function createJWT(payload: JWTPayload, expiresIn?: string): string;
//# sourceMappingURL=jwt.d.ts.map
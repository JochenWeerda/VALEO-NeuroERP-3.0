"use strict";
/**
 * Cryptography Service
 * ISO 27001 A.10 Cryptography Compliance
 * Secure encryption/decryption for Communications Security
 */
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.CryptoService = void 0;
var crypto_1 = require("crypto");
var util_1 = require("util");
var scryptAsync = (0, util_1.promisify)(crypto_1.scrypt);
var CryptoService = /** @class */ (function () {
    function CryptoService() {
        this.algorithm = 'aes-256-gcm';
        this.keySize = 32; // 256 bits
        this.ivSize = 16; // 128 bits
        this.saltSize = 32; // 256 bits
        this.tagSize = 16; // 128 bits
    }
    /**
     * Encrypts data using AES-256-GCM (ISO 27001 A.10.1.1)
     * Provides confidentiality and authenticity
     */
    CryptoService.prototype.encrypt = function (plaintext, keyId) {
        return __awaiter(this, void 0, void 0, function () {
            var salt, iv, key, cipher, encrypted, authTag, encryptedWithTag, error_1;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        _a.trys.push([0, 2, , 3]);
                        salt = (0, crypto_1.randomBytes)(this.saltSize);
                        iv = (0, crypto_1.randomBytes)(this.ivSize);
                        return [4 /*yield*/, this.deriveKey(keyId || 'default', salt)];
                    case 1:
                        key = _a.sent();
                        cipher = (0, crypto_1.createCipheriv)(this.algorithm, key, iv);
                        encrypted = cipher.update(plaintext, 'utf8', 'hex');
                        encrypted += cipher.final('hex');
                        authTag = cipher.getAuthTag();
                        encryptedWithTag = encrypted + ':' + authTag.toString('hex');
                        return [2 /*return*/, {
                                encrypted: encryptedWithTag,
                                iv: iv.toString('hex'),
                                salt: salt.toString('hex'),
                                algorithm: this.algorithm,
                                keyId: keyId || 'default'
                            }];
                    case 2:
                        error_1 = _a.sent();
                        throw new Error("Encryption failed: ".concat(error_1.message));
                    case 3: return [2 /*return*/];
                }
            });
        });
    };
    /**
     * Decrypts data using AES-256-GCM (ISO 27001 A.10.1.1)
     * Verifies authenticity and provides confidentiality
     */
    CryptoService.prototype.decrypt = function (encryptionResult) {
        return __awaiter(this, void 0, void 0, function () {
            var salt, iv, _a, encryptedData, authTagHex, authTag, key, decipher, decrypted, error_2;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        _b.trys.push([0, 2, , 3]);
                        salt = Buffer.from(encryptionResult.salt, 'hex');
                        iv = Buffer.from(encryptionResult.iv, 'hex');
                        _a = encryptionResult.encrypted.split(':'), encryptedData = _a[0], authTagHex = _a[1];
                        authTag = Buffer.from(authTagHex, 'hex');
                        return [4 /*yield*/, this.deriveKey(encryptionResult.keyId, salt)];
                    case 1:
                        key = _b.sent();
                        decipher = (0, crypto_1.createDecipheriv)(this.algorithm, key, iv);
                        decipher.setAuthTag(authTag);
                        decrypted = decipher.update(encryptedData, 'hex', 'utf8');
                        decrypted += decipher.final('utf8');
                        return [2 /*return*/, decrypted];
                    case 2:
                        error_2 = _b.sent();
                        throw new Error("Decryption failed: ".concat(error_2.message));
                    case 3: return [2 /*return*/];
                }
            });
        });
    };
    /**
     * Creates HMAC for data integrity (A.10.1.1)
     * Ensures data has not been tampered with
     */
    CryptoService.prototype.createHmac = function (data_1) {
        return __awaiter(this, arguments, void 0, function (data, keyId) {
            var key, hmac, error_3;
            if (keyId === void 0) { keyId = 'default'; }
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        _a.trys.push([0, 2, , 3]);
                        return [4 /*yield*/, this.getHmacKey(keyId)];
                    case 1:
                        key = _a.sent();
                        hmac = (0, crypto_1.createHmac)('sha256', key);
                        hmac.update(data, 'utf8');
                        return [2 /*return*/, hmac.digest('hex')];
                    case 2:
                        error_3 = _a.sent();
                        throw new Error("HMAC creation failed: ".concat(error_3.message));
                    case 3: return [2 /*return*/];
                }
            });
        });
    };
    /**
     * Verifies HMAC for data integrity (A.10.1.1)
     */
    CryptoService.prototype.verifyHmac = function (data_1, expectedHmac_1) {
        return __awaiter(this, arguments, void 0, function (data, expectedHmac, keyId) {
            var computedHmac, error_4;
            if (keyId === void 0) { keyId = 'default'; }
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        _a.trys.push([0, 2, , 3]);
                        return [4 /*yield*/, this.createHmac(data, keyId)];
                    case 1:
                        computedHmac = _a.sent();
                        // Constant-time comparison to prevent timing attacks
                        return [2 /*return*/, this.constantTimeCompare(computedHmac, expectedHmac)];
                    case 2:
                        error_4 = _a.sent();
                        throw new Error("HMAC verification failed: ".concat(error_4.message));
                    case 3: return [2 /*return*/];
                }
            });
        });
    };
    /**
     * Hashes data using SHA-256 (A.10.1.1)
     * For one-way hashing of passwords, etc.
     */
    CryptoService.prototype.hash = function (data, salt) {
        return __awaiter(this, void 0, void 0, function () {
            var actualSalt, hash;
            return __generator(this, function (_a) {
                try {
                    actualSalt = salt || (0, crypto_1.randomBytes)(this.saltSize).toString('hex');
                    hash = (0, crypto_1.createHash)('sha256');
                    hash.update(data + actualSalt);
                    return [2 /*return*/, {
                            hash: hash.digest('hex'),
                            salt: actualSalt
                        }];
                }
                catch (error) {
                    throw new Error("Hashing failed: ".concat(error.message));
                }
                return [2 /*return*/];
            });
        });
    };
    /**
     * Generates cryptographically secure random data
     * For tokens, IDs, etc. (A.10.1.2)
     */
    CryptoService.prototype.generateSecureRandom = function () {
        return __awaiter(this, arguments, void 0, function (size) {
            if (size === void 0) { size = 32; }
            return __generator(this, function (_a) {
                try {
                    return [2 /*return*/, (0, crypto_1.randomBytes)(size).toString('hex')];
                }
                catch (error) {
                    throw new Error("Random generation failed: ".concat(error.message));
                }
                return [2 /*return*/];
            });
        });
    };
    /**
     * Key rotation functionality (A.10.1.2 Key management)
     * Regularly rotates encryption keys for security
     */
    CryptoService.prototype.rotateKey = function (keyId, tenantId) {
        return __awaiter(this, void 0, void 0, function () {
            var newKeyMetadata;
            return __generator(this, function (_a) {
                try {
                    newKeyMetadata = {
                        keyId: "".concat(keyId, "-").concat(Date.now()),
                        algorithm: this.algorithm,
                        keySize: this.keySize,
                        purpose: 'ENCRYPTION',
                        createdAt: new Date(),
                        expiresAt: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000), // 1 year
                        status: 'ACTIVE',
                        tenantId: tenantId
                    };
                    // In real implementation, would store in secure key management system
                    console.log("Key rotated: ".concat(newKeyMetadata.keyId, " for tenant ").concat(tenantId));
                    return [2 /*return*/, newKeyMetadata];
                }
                catch (error) {
                    throw new Error("Key rotation failed: ".concat(error.message));
                }
                return [2 /*return*/];
            });
        });
    };
    /**
     * Validates encryption strength meets ISO 27001 requirements
     */
    CryptoService.prototype.validateEncryptionStandards = function (algorithm, keySize) {
        var approvedAlgorithms = [
            'aes-256-gcm', 'aes-256-cbc', 'aes-192-gcm',
            'chacha20-poly1305'
        ];
        var minimumKeySizes = {
            'aes-256-gcm': 256,
            'aes-256-cbc': 256,
            'aes-192-gcm': 192,
            'chacha20-poly1305': 256
        };
        return approvedAlgorithms.includes(algorithm) &&
            keySize >= minimumKeySizes[algorithm];
    };
    // Private helper methods
    CryptoService.prototype.deriveKey = function (keyId, salt) {
        return __awaiter(this, void 0, void 0, function () {
            var masterKey, derivedKey;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.getMasterKey(keyId)];
                    case 1:
                        masterKey = _a.sent();
                        return [4 /*yield*/, scryptAsync(masterKey, salt, this.keySize)];
                    case 2:
                        derivedKey = _a.sent();
                        return [2 /*return*/, derivedKey];
                }
            });
        });
    };
    CryptoService.prototype.getMasterKey = function (keyId) {
        return __awaiter(this, void 0, void 0, function () {
            var masterKeys;
            return __generator(this, function (_a) {
                masterKeys = {
                    'default': process.env.CRYPTO_MASTER_KEY || 'default-master-key-for-dev-only',
                    'sales': process.env.SALES_CRYPTO_KEY || 'sales-master-key-for-dev-only',
                    'delivery': process.env.DELIVERY_CRYPTO_KEY || 'delivery-master-key-for-dev-only'
                };
                return [2 /*return*/, masterKeys[keyId] || masterKeys['default']];
            });
        });
    };
    CryptoService.prototype.getHmacKey = function (keyId) {
        return __awaiter(this, void 0, void 0, function () {
            var hmacKeys;
            return __generator(this, function (_a) {
                hmacKeys = {
                    'default': process.env.HMAC_KEY || 'default-hmac-key-for-dev-only'
                };
                return [2 /*return*/, hmacKeys[keyId] || hmacKeys['default']];
            });
        });
    };
    CryptoService.prototype.constantTimeCompare = function (a, b) {
        if (a.length !== b.length) {
            return false;
        }
        var result = 0;
        for (var i = 0; i < a.length; i++) {
            result |= a.charCodeAt(i) ^ b.charCodeAt(i);
        }
        return result === 0;
    };
    return CryptoService;
}());
exports.CryptoService = CryptoService;

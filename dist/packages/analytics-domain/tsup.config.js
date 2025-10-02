"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const tsup_1 = require("tsup");
exports.default = (0, tsup_1.defineConfig)({
    entry: ['src/index.ts'],
    format: ['cjs', 'esm'],
    dts: true,
    splitting: false,
    sourcemap: true,
    clean: true,
    external: [
        '@valero-neuroerp/data-models',
        '@valero-neuroerp/utilities',
        '@valero-neuroerp/business-rules'
    ],
    treeshake: true,
});

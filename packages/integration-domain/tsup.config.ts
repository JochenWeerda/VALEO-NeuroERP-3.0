import { defineConfig } from 'tsup';

export default defineConfig({
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


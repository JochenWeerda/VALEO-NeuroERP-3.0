import { describe, expect, it } from 'vitest'
import { validTextFileContract, validTextFileDefinitions, validTextFileValue, readTextFile } from '@/components/mask-builder/runtime/text-file-contract'
import { validateScreenDefinition, type ScreenDefinition, type ScreenFieldDefinition } from '@/components/mask-builder/schema'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { renderPlanToScreenDefinition } from '@/components/mask-builder/render-plan/plan-to-screen'
const contract = { encoding: 'utf-8' as const, maxBytes: 16, accept: ['.csv' as const, '.txt' as const] }
const field: ScreenFieldDefinition = { key: 'csv', label: 'Datei', type: 'file', required: true, fileContent: contract }
const definition: ScreenDefinition = { schemaVersion: 1, id: 'test/file-content', title: 'Datei', mode: 'detail', domain: 'sales', fields: [field] }
describe('text-file metadata', () => {
  it('rejects malformed contracts', () => {
    for (const value of [null, false, [], {}, { ...contract, maxBytes: 0 }, { ...contract, maxBytes: true }, { ...contract, maxBytes: 1.5 },
    { ...contract, maxBytes: 1048577 }, { ...contract, encoding: 'UTF-8' }, { ...contract, encoding: 'utf-16' },
    { ...contract, accept: [] }, { ...contract, accept: ['.CSV'] }, { ...contract, accept: ['text/csv'] },
    { ...contract, accept: ['.csv', '.csv'] }, { ...contract, accept: [{}] }, { ...contract, accept: [null] },
    { ...contract, uploadEndpoint: '/upload' }, undefined,
  ]) {
    expect(validTextFileContract(value, 'file')).toBe(false)
    expect(validateScreenDefinition({ ...definition, fields: [{ ...field, fileContent: value } as ScreenFieldDefinition] })).toContain('fileContent is invalid')
    }
  })
  it('permits legacy fields, byte boundaries and valid declarations', () => {
    expect(validTextFileDefinitions({ fields: [{ type: 'file' }] })).toBe(true)
    expect(validTextFileContract({ ...contract, maxBytes: 1 }, 'file')).toBe(true)
    expect(validTextFileContract({ ...contract, maxBytes: 1048576 }, 'file')).toBe(true)
    expect(validTextFileContract(contract, 'text')).toBe(false)
  })
  it('validates every input container', () => {
    for (const container of [
    (f: object) => ({ fields: [f] }), (f: object) => ({ tabs: [{ fields: [f] }] }),
    (f: object) => ({ actions: [{ inputFields: [f] }] }), (f: object) => ({ tables: [{ rowActions: [{ inputFields: [f] }] }] }),
    (f: object) => ({ fields: [{ type: 'table', rowFields: [f] }] }),
  ]) {
    expect(validTextFileDefinitions(container(field))).toBe(true)
    expect(validTextFileDefinitions(container({ ...field, fileContent: null }))).toBe(false)
    }
  })
  it('preserves root and tab metadata through compilation and projection', () => {
    const plan = compileRenderPlanFromScreenDefinition({ ...definition, tabs: [{ key: 'files', label: 'Dateien', fields: [{ ...field, key: 'tabFile' }] }] })
    expect(plan.fieldsByKey.csv.fileContent).toEqual(contract)
    const projected = renderPlanToScreenDefinition(plan)
    expect(projected.fields?.[0].fileContent).toEqual(contract)
    expect(projected.tabs?.[0].fields?.[0].fileContent).toEqual(contract)
  })
  it('rejects invalid metadata before cache access and recompiles changed limits', () => {
    expect(compileRenderPlanFromScreenDefinition(definition).fieldsByKey.csv.fileContent?.maxBytes).toBe(16)
    expect(compileRenderPlanFromScreenDefinition({ ...definition, fields: [{ ...field, fileContent: { ...contract, maxBytes: 8 } }] }).fieldsByKey.csv.fileContent?.maxBytes).toBe(8)
    expect(() => compileRenderPlanFromScreenDefinition({ ...definition, actions: [{ key: 'import', label: 'Import', inputFields: [{ ...field, fileContent: null } as unknown as ScreenFieldDefinition] }] })).toThrow('Invalid text file content contract')
  })
})
describe('text-file contents', () => {
  it('rejects unsafe direct values', () => {
    for (const value of [null, 12, {}, new Blob(['x']), '\uD800', '\uDC00', 'binary\u0000', 'x'.repeat(17), '€'.repeat(6), '']) {
    expect(validTextFileValue(field, value)).toBe(false)
    }
  })
  it('measures UTF-8 bytes and blocks pending/invalid optional selections', () => {
    expect(validTextFileValue(field, '€'.repeat(5))).toBe(true)
    expect(validTextFileValue(field, 'x'.repeat(16))).toBe(true)
    expect(validTextFileValue(field, '🙂')).toBe(true)
    expect(validTextFileValue({ ...field, required: false }, '')).toBe(true)
    expect(validTextFileValue({ ...field, required: false }, undefined)).toBe(true)
    expect(validTextFileValue({ ...field, required: false }, null)).toBe(false)
  })
  it('reads CSV/TXT independently of MIME and handles UTF-8 BOM', async () => {
    expect(await readTextFile(new File(['ä;1\n'], 'LISTE.CSV', { type: 'application/octet-stream' }), contract)).toBe('ä;1\n')
    expect(await readTextFile(new File([new Uint8Array([239, 187, 191, 97])], 'list.txt'), contract)).toBe('a')
  })
  it('rejects invalid bytes or extensions', async () => {
    for (const file of [new File(['text'], 'file.pdf'), new File([], 'file.csv'), new File(['x'.repeat(17)], 'file.txt'),
    new File([new Uint8Array([0xc3, 0x28])], 'file.csv'), new File(['a\u0000'], 'file.csv'),
  ]) { await expect(readTextFile(file, contract)).rejects.toThrow() }
  })
})

import type { ScreenFieldDefinition, TextFileContentContract } from '../schema'

export const MAX_TEXT_FILE_BYTES = 1_048_576

export function validTextFileContract(value: unknown, fieldType: unknown): value is TextFileContentContract {
  if (fieldType !== 'file' || !value || typeof value !== 'object' || Array.isArray(value)) return false
  const item = value as Record<string, unknown>
  return Object.keys(item).length === 3 && Object.keys(item).every(key => ['encoding', 'maxBytes', 'accept'].includes(key))
    && item.encoding === 'utf-8' && typeof item.maxBytes === 'number' && Number.isInteger(item.maxBytes)
    && item.maxBytes > 0 && item.maxBytes <= MAX_TEXT_FILE_BYTES
    && Array.isArray(item.accept) && item.accept.length > 0 && item.accept.length <= 2
    && new Set(item.accept).size === item.accept.length && item.accept.every(extension => extension === '.csv' || extension === '.txt')
}

/** JSON metadata may contain fields in tabs, tables or action inputs. */
export function validTextFileDefinitions(value: unknown): boolean {
  if (!value || typeof value !== 'object') return true
  if (Array.isArray(value)) return value.every(validTextFileDefinitions)
  const node = value as Record<string, unknown>
  if (Object.prototype.hasOwnProperty.call(node, 'fileContent') && !validTextFileContract(node.fileContent, node.type)) return false
  return Object.values(node).every(validTextFileDefinitions)
}

export function validTextFileValue(field: ScreenFieldDefinition, value: unknown): boolean {
  if (!validTextFileContract(field.fileContent, field.type)) return false
  // null is the transient pending/invalid selection. It must block optional fields too.
  if (value === undefined || value === '') return !field.required
  if (typeof value !== 'string' || value.length > field.fileContent.maxBytes) return false
  // TextEncoder replaces malformed surrogates; reject those before measuring bytes.
  if (/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/u.test(value)) return false
  for (const character of value) {
    const code = character.charCodeAt(0)
    if ((code < 32 && ![9, 10, 13].includes(code)) || code === 127) return false
  }
  return new TextEncoder().encode(value).byteLength <= field.fileContent.maxBytes
}

export async function readTextFile(file: File, contract: TextFileContentContract): Promise<string> {
  if (!validTextFileContract(contract, 'file')) throw new Error('Die Dateivorgaben sind ungültig.')
  if (!contract.accept.some(extension => file.name.toLowerCase().endsWith(extension))) {
    throw new Error(`Bitte eine Datei mit ${contract.accept.join(' oder ')} auswählen.`)
  }
  if (file.size < 1 || file.size > contract.maxBytes) throw new Error(`Die Datei muss 1 bis ${contract.maxBytes} Bytes enthalten.`)
  const bytes = await new Promise<ArrayBuffer>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => reader.result instanceof ArrayBuffer ? resolve(reader.result) : reject(new Error('Die Datei konnte nicht gelesen werden.'))
    reader.onerror = () => reject(new Error('Die Datei konnte nicht gelesen werden.'))
    reader.onabort = () => reject(new Error('Das Lesen der Datei wurde abgebrochen.'))
    reader.readAsArrayBuffer(file)
  })
  if (bytes.byteLength < 1 || bytes.byteLength > contract.maxBytes) throw new Error('Die Dateigröße ist ungültig.')
  let text: string
  try { text = new TextDecoder('utf-8', { fatal: true }).decode(bytes) } catch { throw new Error('Die Datei muss gültigen UTF-8-Text enthalten.') }
  if (!text || !validTextFileValue({ key: 'file', label: 'Datei', type: 'file', required: true, fileContent: contract }, text)) {
    throw new Error('Die Datei enthält keinen gültigen Text oder unzulässige Steuerzeichen.')
  }
  return text
}

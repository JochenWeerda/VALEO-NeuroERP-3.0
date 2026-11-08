import { expect, it } from 'vitest'
import { readCompleteList } from './list-client-source'
it('collects the full declared result before client pagination or export', async () => {
  const requested: number[] = []
  const result = await readCompleteList(async page => { requested.push(page); return { items: Array.from({length: page === 1 ? 100 : 27}, (_, i) => ({ id: String((page - 1) * 100 + i) })), total: 127 } })
  expect(requested).toEqual([1, 2]); expect(result.items).toHaveLength(127)
})
it('rejects changing totals, duplicate rows and incomplete sources', async () => {
  for (const second of [{items:[{id:'b'}],total:3},{items:[{id:'a'}],total:2},{items:[],total:2}]) {
    await expect(readCompleteList(async page => page === 1 ? {items:[{id:'a'}],total:2} : second)).rejects.toThrow()
  }
})
it('rejects oversized or invalid totals', async () => {
  for (const total of [-1, 5001, Number.NaN]) await expect(readCompleteList(async () => ({items:[],total}))).rejects.toThrow()
})

it('stops further page requests when the screen query is cancelled', async () => {
  const controller = new AbortController()
  let requests = 0
  await expect(readCompleteList(async () => { requests += 1; controller.abort(); return { items:[{id:'a'}], total:2 } }, controller.signal)).rejects.toMatchObject({name:'AbortError'})
  expect(requests).toBe(1)
})

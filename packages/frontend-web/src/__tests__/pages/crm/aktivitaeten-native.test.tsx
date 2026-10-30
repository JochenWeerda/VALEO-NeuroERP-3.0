import '@testing-library/jest-dom/vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import Page from '@/pages/crm/aktivitaeten'
import definition from '../../fixtures/crm-activities-studio.json'

const state=vi.hoisted(()=>({get:vi.fn(),navigate:vi.fn(),failed:false}))
vi.mock('@/lib/api-client',()=>({apiClient:{get:state.get,request:vi.fn()},getAxiosErrorMessage:(e:Error)=>e.message}))
vi.mock('@/app/routing/typed-router',()=>({useNavigate:()=>state.navigate}))
vi.mock('@/hooks/useAuth',()=>({useAuth:()=>({user:{sub:'human-a',roles:['CRM_BEARBEITEN'],scopes:[]}})}))
vi.mock('@/hooks/useTouchDevice',()=>({useTouchDevice:()=>false}))
vi.mock('@/hooks/useKeyboardShortcuts',()=>({buildCoreMaskShortcuts:()=>[],useKeyboardShortcuts:()=>undefined}))
vi.mock('@/hooks/use-toast',()=>({useToast:()=>({toast:vi.fn()})}))
vi.mock('@/lib/api/ux-overlays',()=>({overlayKeys:{screen:(id:string)=>['overlays',id]},
  useUserScreenOverlay:()=>({data:{overlay:{},schema_version:1}}),saveUserOverlay:vi.fn(),deleteUserOverlay:vi.fn()}))

function setup(){
  const rows=Array.from({length:127},(_,n)=>({id:String(n+1),type:'call',title:`SYNTH-${String(n+1).padStart(3,'0')}`,
    customer:`CUSTOMER-${n+1}`,contact_person:'Synthetic',assigned_to:n===126?'human-a':'other',
    date:n===126?'2026-10-01T10:00:00Z':null,status:'planned',overdue:n===126}))
  state.get.mockImplementation(async(url:string)=>{
    if(url==='/api/v1/masks/crm__aktivitaeten-liste/screen-definition')return{data:definition}
    if(url.startsWith('/api/v1/masks/crm%2Faktivitaeten-liste/data/list?')){
      if(state.failed)throw new Error('Synthetic CRM failure')
      const params=new URLSearchParams(url.split('?')[1]);expect(params.get('complete')).toBe('true')
      expect(params.has('tenant_id')).toBe(false);expect(params.has('actor')).toBe(false)
      const presets=JSON.parse(params.get('preset_filters')??'{}')
      let selected=rows
      if(presets.owner==='mine')selected=selected.filter(row=>row.assigned_to==='human-a')
      if(presets.when==='overdue')selected=selected.filter(row=>row.overdue)
      return{data:{data:{items:selected,total:selected.length}}}
    }
    throw new Error(`Unexpected source ${url}`)
  })
  const client=new QueryClient({defaultOptions:{queries:{retry:false}}})
  render(<QueryClientProvider client={client}><Page/></QueryClientProvider>)
}

beforeEach(()=>{vi.clearAllMocks();state.failed=false})

describe('Studio CRM activities canonical runtime',()=>{
  it('collects once, searches across all pages and navigates to the canonical detail',async()=>{
    const pushState=vi.spyOn(window.history,'pushState')
    setup()
    expect(await screen.findByText('Seite 1 / 3')).toBeInTheDocument()
    const calls=()=>state.get.mock.calls.filter(([url])=>String(url).includes('/data/list?'))
    expect(calls()).toHaveLength(1)
    fireEvent.change(screen.getByTestId('search-list'),{target:{value:'CUSTOMER-127'}})
    expect(await screen.findAllByText('SYNTH-127')).not.toHaveLength(0)
    expect(screen.queryByText('SYNTH-001')).toBeNull()
    expect(calls()).toHaveLength(1)
    fireEvent.click(screen.getByRole('button',{name:'In Vollansicht öffnen'}))
    expect(pushState).toHaveBeenCalledWith(null,'','/crm/aktivitaet/127')
  })
  it('sends registered owner/calendar selections and keeps them combined',async()=>{
    setup();await screen.findByText('Seite 1 / 3')
    fireEvent.change(screen.getByRole('combobox',{name:'Zustaendigkeit'}),{target:{value:'mine'}})
    await waitFor(()=>expect(screen.queryByText('SYNTH-001')).toBeNull())
    fireEvent.change(screen.getByRole('combobox',{name:'Zeitraum'}),{target:{value:'overdue'}})
    await waitFor(()=>{
      const urls=state.get.mock.calls.map(([url])=>String(url)).filter(url=>url.includes('/data/list?'))
      const presets=JSON.parse(new URLSearchParams(urls.at(-1)!.split('?')[1]).get('preset_filters')!)
      expect(presets).toEqual({owner:'mine',when:'overdue'})
    })
    expect(screen.getAllByText('SYNTH-127').length).toBeGreaterThan(0)
  })
  it('exports the full filtered data rather than the first source page',async()=>{
    let blob:Blob|undefined
    vi.stubGlobal('URL',{...URL,createObjectURL:vi.fn((data:Blob)=>{blob=data;return'blob:crm'}),revokeObjectURL:vi.fn()})
    vi.spyOn(HTMLAnchorElement.prototype,'click').mockImplementation(()=>undefined)
    setup();await screen.findByText('Seite 1 / 3')
    fireEvent.change(screen.getByTestId('search-list'),{target:{value:'CUSTOMER-127'}})
    await screen.findAllByText('SYNTH-127')
    fireEvent.click(screen.getByRole('button',{name:'CSV-Export'}))
    await waitFor(()=>expect(blob).toBeDefined())
    const text=await new Promise<string>(resolve=>{const reader=new FileReader();reader.onload=()=>resolve(String(reader.result));reader.readAsText(blob!)})
    expect(text).toContain('SYNTH-127');expect(text).not.toContain('SYNTH-001')
    vi.unstubAllGlobals();vi.restoreAllMocks()
  })
})

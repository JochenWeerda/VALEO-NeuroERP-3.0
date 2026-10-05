# Read-only L3 dropdown leaf capture (RDP 10.200.1.3).
param(
    [string]$OutDir = "$env:USERPROFILE\Pictures\L3-Capture-2026-08-22-dropdown-leaves"
)

$ErrorActionPreference = 'Stop'

Add-Type -ReferencedAssemblies System.Drawing @"
using System; using System.Runtime.InteropServices; using System.Drawing; using System.Drawing.Imaging;
public class RdpLeaf {
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
  public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder lpString, int nMaxCount);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int X, int Y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
  [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  public const uint MOUSE_LEFTDOWN = 0x0002; public const uint MOUSE_LEFTUP = 0x0004;
  public static void LeftClick(int x,int y){ SetCursorPos(x,y); mouse_event(MOUSE_LEFTDOWN,0,0,0,UIntPtr.Zero); mouse_event(MOUSE_LEFTUP,0,0,0,UIntPtr.Zero); }
}
"@

Add-Type -AssemblyName System.Windows.Forms

function Get-RdpHwnd {
    $script:best = [IntPtr]::Zero
    $script:bestArea = 0
    $cb = [RdpLeaf+EnumWindowsProc]{
        param([IntPtr]$hwnd, [IntPtr]$lp)
        $sb = New-Object System.Text.StringBuilder 512
        [RdpLeaf]::GetWindowText($hwnd, $sb, 512) | Out-Null
        $t = $sb.ToString()
        if ($t -match '10\.200\.1\.3|Remotedesktopverbindung') {
            $r = New-Object RdpLeaf+RECT
            [RdpLeaf]::GetWindowRect($hwnd, [ref]$r) | Out-Null
            $area = ($r.Right - $r.Left) * ($r.Bottom - $r.Top)
            if ($area -gt $script:bestArea) { $script:bestArea = $area; $script:best = $hwnd }
        }
        return $true
    }
    [RdpLeaf]::EnumWindows($cb, [IntPtr]::Zero) | Out-Null
    if ($script:best -eq [IntPtr]::Zero) { throw 'Kein RDP-Fenster. Bitte zuerst verbinden.' }
    return $script:best
}

function Get-WinOrigin([IntPtr]$hwnd) {
    $r = New-Object RdpLeaf+RECT
    [RdpLeaf]::GetWindowRect($hwnd, [ref]$r) | Out-Null
    return @{ X = $r.Left; Y = $r.Top; W = ($r.Right - $r.Left); H = ($r.Bottom - $r.Top) }
}

function Save-Shot([IntPtr]$hwnd, [string]$path) {
    [RdpLeaf]::SetForegroundWindow($hwnd) | Out-Null
    Start-Sleep -Milliseconds 150
    $r = New-Object RdpLeaf+RECT
    [RdpLeaf]::GetWindowRect($hwnd, [ref]$r) | Out-Null
    $w = $r.Right - $r.Left; $h = $r.Bottom - $r.Top
    if ($w -lt 100 -or $h -lt 100) { throw "Fenster zu klein: ${w}x${h}" }
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($r.Left, $r.Top, 0, 0, [System.Drawing.Size]::new($w, $h))
    $g.Dispose()
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
}

function Click-Rel([hashtable]$o, [int]$x, [int]$y, [int]$ms = 800) {
    [RdpLeaf]::LeftClick($o.X + $x, $o.Y + $y)
    Start-Sleep -Milliseconds $ms
}

function Close-Mdi {
    for ($i = 0; $i -lt 5; $i++) {
        [System.Windows.Forms.SendKeys]::SendWait('{ESC}')
        Start-Sleep -Milliseconds 100
        [System.Windows.Forms.SendKeys]::SendWait('^{F4}')
        Start-Sleep -Milliseconds 200
    }
}

function Open-Menu {
    param([hashtable]$o, [int]$tabX, [int]$iconX, [int]$iconY = 108)
    Click-Rel $o $tabX 58 350
    Click-Rel $o $tabX 58 250
    Click-Rel $o $iconX $iconY 550
}

function Capture-Leaves {
    param(
        [IntPtr]$hwnd, [hashtable]$o, [string]$Log,
        [string]$Prefix, [int]$tabX, [int]$iconX,
        [string[]]$Leaves, [int]$startY = 133, [int]$stepY = 22, [int]$clickX = 175, [int]$waitMs = 1300
    )
    $menuPath = Join-Path $OutDir "${Prefix}_menu_open.png"
    if ((-not (Test-Path $menuPath)) -or ($Prefix -match '^(beleg|aw_weitere|aw_artikel|aw_lager)$')) {
        Open-Menu $o $tabX $iconX
        Save-Shot $hwnd $menuPath
    }
    $i = 0
    foreach ($leaf in $Leaves) {
        $leafPath = Join-Path $OutDir "${Prefix}_leaf_${i}_${leaf}.png"
        if ((Test-Path $leafPath) -and $Prefix -notmatch '^(beleg|aw_weitere|aw_artikel|aw_lager|fav)') { $i++; continue }
        Open-Menu $o $tabX $iconX
        $y = $startY + ($i * $stepY)
        Click-Rel $o $clickX $y $waitMs
        Save-Shot $hwnd $leafPath
        "ok $Prefix $leaf y=$y" | Add-Content $Log
        Close-Mdi
        $i++
    }
}

$TabAw = 660; $TabSi = 760; $TabErf = 370; $TabPrd = 620; $TabFav = 175

# Icon X @ Y=108 — kalibriert 2026-08-22 (Ribbon mit Gruppe Überwachung)
$IconsAw = @{
    AbfrageCenter  = 165
    BelegKontrolle = 215
    Dokumenten     = 292
    Kunden         = 358
    Lieferant      = 403
    Artikel        = 448
    Lager          = 493
    Ernte          = 538
    Vertreter      = 583
    Strecke        = 628
    Weitere        = 673
}
$IconsPrd = @{ Chargen = 545 }
$IconsFav = @{ ArtikelKonto = 290; VerkaufLs = 175; ArtikelStamm = 220 }

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$log = Join-Path $OutDir 'leaf-log.txt'
"start $(Get-Date -Format o)" | Set-Content $log

$hwnd = Get-RdpHwnd
[RdpLeaf]::ShowWindow($hwnd, 3) | Out-Null
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
[RdpLeaf]::MoveWindow($hwnd, -8, -8, $screen.Width + 16, $screen.Height + 16, $true) | Out-Null
[RdpLeaf]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -Milliseconds 800
$o = Get-WinOrigin $hwnd
"origin $($o.X),$($o.Y) size $($o.W)x$($o.H)" | Add-Content $log
Save-Shot $hwnd (Join-Path $OutDir '_probe.png')
Close-Mdi

Capture-Leaves $hwnd $o $log 'beleg' $TabAw $IconsAw.BelegKontrolle @(
    'unerledigte_bestellungen','eingangsls_kontrolle','auftrags_kontrolle',
    'lieferschein_kontrolle','gesperrte_ls','nicht_fakturierte'
)

Capture-Leaves $hwnd $o $log 'aw_weitere' $TabAw $IconsAw.Weitere @(
    'volltextsuche_dms','fracht','bonus_berechnung','genossenschaften',
    'terror_personal','terror_kunden','aenderungshistorie','duengemittelmengen'
)

Capture-Leaves $hwnd $o $log 'aw_artikel' $TabAw $IconsAw.Artikel @(
    'artikel_auswertung','chefauswertung_gruppen','verrechnungspreis_lager',
    'aenderungen_ek_preise','aktions_auswertung','uebersicht_bewegungen',
    'artikel_umsaetze','artikel_konto','artikel_konto_druck','lager_dispo',
    'suche_biete','getreidemeldung','mvo_meldung','tagesabschluss_journal'
) -waitMs 1500

Capture-Leaves $hwnd $o $log 'aw_lager' $TabAw $IconsAw.Lager @(
    'auswertung_chargen_nummern','bestandsbewertung_charge','rueckverfolgung_verwendung'
)

Capture-Leaves $hwnd $o $log 'si_mde' $TabSi 215 @('datenuebernahme','verarbeitung')

Capture-Leaves $hwnd $o $log 'erf_kontrakt' $TabErf 95 @('einkauf','zukauf','verkauf')

Capture-Leaves $hwnd $o $log 'prd_chargen' $TabPrd $IconsPrd.Chargen @('chargen_nummern_bearbeiten')

Click-Rel $o $TabFav 58 450
Click-Rel $o $IconsFav.ArtikelKonto 108 1500
Save-Shot $hwnd (Join-Path $OutDir 'fav_artikel_konto_direct.png')
'ok fav artikel_konto direct' | Add-Content $log
Close-Mdi

$count = (Get-ChildItem $OutDir -Filter '*.png').Count
"end $(Get-Date -Format o) pngs=$count" | Add-Content $log
Write-Host "Fertig: $OutDir ($count PNGs)"

param(
  [string]$OutDir = "$env:USERPROFILE\Pictures\L3-Capture-2026-08-22-dropdown-leaves",
  [int[]]$OnlyIndex = @(0, 1, 2, 3, 4, 5),
  [switch]$SkipReset
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type -ReferencedAssemblies System.Drawing @"
using System; using System.Runtime.InteropServices; using System.Drawing;
public class L3Bl {
  public delegate bool EP(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EP cb, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, System.Text.StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int X, int Y, int W, int H, bool r);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
  public static void Click(int x,int y){ SetCursorPos(x,y); mouse_event(2,0,0,0,UIntPtr.Zero); mouse_event(4,0,0,0,UIntPtr.Zero);} }
"@

$refW = 1936; $refH = 1048
$hwnd = [IntPtr]::Zero; $best = 0
[L3Bl]::EnumWindows([L3Bl+EP]{
  param($h, $l)
  $sb = New-Object System.Text.StringBuilder 512
  [L3Bl]::GetWindowText($h, $sb, 512) | Out-Null
  if ($sb.ToString() -match '10\.200\.1\.3') {
    $r = New-Object L3Bl+RECT
    [L3Bl]::GetWindowRect($h, [ref]$r) | Out-Null
    $a = ($r.R - $r.L) * ($r.B - $r.T)
    if ($a -gt $script:best) { $script:best = $a; $script:hwnd = $h }
  }
  return $true
}, [IntPtr]::Zero) | Out-Null
if ($hwnd -eq [IntPtr]::Zero) { throw 'Kein RDP-Fenster 10.200.1.3' }

$s = [Windows.Forms.Screen]::PrimaryScreen.Bounds
[L3Bl]::ShowWindow($hwnd, 3) | Out-Null
[L3Bl]::MoveWindow($hwnd, -8, -8, $s.Width + 16, $s.Height + 16, $true) | Out-Null
Start-Sleep -Milliseconds 700

function Sync-Origin {
  $script:r = New-Object L3Bl+RECT
  [L3Bl]::GetWindowRect($hwnd, [ref]$script:r) | Out-Null
  $script:ox = $script:r.L; $script:oy = $script:r.T
  $script:ww = $script:r.R - $script:r.L; $script:wh = $script:r.B - $script:r.T
  $script:sx = $ww / $refW; $script:sy = $wh / $refH
  $script:yExtra = 0
  if ($wh -ge 1060) { $script:yExtra = [int](($wh - $refH) * 0.45) }
}
Sync-Origin
if ($ww -lt 1200) { throw "RDP zu klein (${ww}x${wh})" }

function Click-Rel([int]$x, [int]$y, [int]$ms = 350) {
  Sync-Origin
  $px = [int][math]::Round($x * $sx)
  $py = [int][math]::Round($y * $sy) + $yExtra
  [L3Bl]::Click($ox + $px, $oy + $py)
  Start-Sleep -Milliseconds $ms
}

function Shot([string]$path) {
  Sync-Origin
  $bmp = New-Object Drawing.Bitmap $ww, $wh
  $g = [Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($ox, $oy, 0, 0, [Drawing.Size]::new($ww, $wh))
  $g.Dispose()
  $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
  $bmp.Dispose()
}

function Tab-Aw {
  # Tab-Textzeile (Y=48), nicht Icon-Zeile
  Click-Rel 660 48 300
  Click-Rel 660 48 220
}

function Close-ErrorDialog {
  Click-Rel 960 555 350
}

function Close-LeafOnly {
  Click-Rel 1875 198 300
}

$leaves = @(
  'unerledigte_bestellungen','eingangsls_kontrolle','auftrags_kontrolle',
  'lieferschein_kontrolle','gesperrte_ls','nicht_fakturierte'
)

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$log = Join-Path $OutDir 'beleg-leaf-run-log.txt'
"start $(Get-Date -Format o) size=${ww}x${wh} sx=$sx sy=$sy yExtra=$yExtra" | Set-Content $log

Close-ErrorDialog
if (-not $SkipReset) {
  Click-Rel 1875 198 300
  Click-Rel 1875 198 300
}

Tab-Aw
Shot (Join-Path $OutDir '_tab_aw_check.png')
Click-Rel 215 108 550
Shot (Join-Path $OutDir 'beleg_menu_open_run.png')

foreach ($i in $OnlyIndex) {
  if ($i -lt 0 -or $i -ge $leaves.Count) { continue }
  $leaf = $leaves[$i]
  $out = Join-Path $OutDir "beleg_leaf_run_${i}_${leaf}.png"

  if ($i -gt 0) { Close-LeafOnly }
  Close-ErrorDialog
  Tab-Aw
  Click-Rel 215 108 550
  $menuY = 133 + ($i * 22)

  if ($i -in 2, 3) {
    Click-Rel 175 $menuY 450
    Click-Rel 355 ($menuY + 22) 2200
  } else {
    Click-Rel 175 $menuY 2200
  }

  Shot $out
  "ok idx=$i menuY=$menuY -> $out" | Add-Content $log
}

"end $(Get-Date -Format o)" | Add-Content $log
Write-Host "Beleg leaves done -> $OutDir"

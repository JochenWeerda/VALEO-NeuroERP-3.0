$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System; using System.Runtime.InteropServices; using System.Drawing;
public class L3Probe {
  public delegate bool EP(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EP cb, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, System.Text.StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int X, int Y, int W, int H, bool r);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
}
"@
$hwnd = [IntPtr]::Zero; $best = 0
[L3Probe]::EnumWindows([L3Probe+EP]{
  param($h, $l)
  $sb = New-Object System.Text.StringBuilder 512
  [L3Probe]::GetWindowText($h, $sb, 512) | Out-Null
  if ($sb.ToString() -match '10\.200\.1\.3') {
    $r = New-Object L3Probe+RECT
    [L3Probe]::GetWindowRect($h, [ref]$r) | Out-Null
    $a = ($r.R - $r.L) * ($r.B - $r.T)
    if ($a -gt $script:best) { $script:best = $a; $script:hwnd = $h }
  }
  return $true
}, [IntPtr]::Zero) | Out-Null
if ($hwnd -eq [IntPtr]::Zero) { throw 'Kein RDP-Fenster 10.200.1.3' }

$s = [Windows.Forms.Screen]::PrimaryScreen.Bounds
[L3Probe]::ShowWindow($hwnd, 3) | Out-Null
[L3Probe]::MoveWindow($hwnd, -8, -8, $s.Width + 16, $s.Height + 16, $true) | Out-Null
Start-Sleep -Milliseconds 700

$r = New-Object L3Probe+RECT
[L3Probe]::GetWindowRect($hwnd, [ref]$r) | Out-Null
$w = $r.R - $r.L; $h = $r.B - $r.T
if ($w -lt 1200) { throw "RDP zu klein (${w}x${h}) - bitte maximieren." }

$bmp = New-Object Drawing.Bitmap $w, $h
$g = [Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($r.L, $r.T, 0, 0, [Drawing.Size]::new($w, $h))
$g.Dispose()
$out = "$env:USERPROFILE\Pictures\L3-Capture-2026-08-22-dropdown-leaves\_probe_now.png"
New-Item -ItemType Directory -Force -Path (Split-Path $out) | Out-Null
$bmp.Save($out); $bmp.Dispose()
Write-Host "saved $out ${w}x${h}"

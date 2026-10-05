# Tab-Kalibrierung: findet AUSWERTUNGEN auf aktueller Aufloesung
param([string]$OutDir = "$env:USERPROFILE\Pictures\L3-Capture-2026-08-22-dropdown-leaves")
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type -ReferencedAssemblies System.Drawing @"
using System; using System.Runtime.InteropServices; using System.Drawing;
public class L3Tc {
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
$hwnd=[IntPtr]::Zero;$best=0
[L3Tc]::EnumWindows([L3Tc+EP]{param($h,$l)$sb=New-Object System.Text.StringBuilder 512;[L3Tc]::GetWindowText($h,$sb,512)|Out-Null;if($sb.ToString()-match '10\.200\.1\.3'){$r=New-Object L3Tc+RECT;[L3Tc]::GetWindowRect($h,[ref]$r)|Out-Null;$a=($r.R-$r.L)*($r.B-$r.T);if($a -gt $script:best){$script:best=$a;$script:hwnd=$h}};return $true},[IntPtr]::Zero)|Out-Null
$s=[Windows.Forms.Screen]::PrimaryScreen.Bounds
[L3Tc]::ShowWindow($hwnd,3)|Out-Null
[L3Tc]::MoveWindow($hwnd,-8,-8,$s.Width+16,$s.Height+16,$true)|Out-Null
Start-Sleep 700
function Sync{$script:rr=New-Object L3Tc+RECT;[L3Tc]::GetWindowRect($hwnd,[ref]$rr)|Out-Null;$script:ox=$rr.L;$script:oy=$rr.T;$script:ww=$rr.R-$rr.L;$script:wh=$rr.B-$rr.T}
function C($x,$y,$ms=300){Sync;[L3Tc]::Click($ox+$x,$oy+$y);Start-Sleep -Milliseconds $ms}
function Shot($p){Sync;$b=New-Object Drawing.Bitmap $ww,$wh;$g=[Drawing.Graphics]::FromImage($b);$g.CopyFromScreen($ox,$oy,0,0,[Drawing.Size]::new($ww,$wh));$g.Dispose();$b.Save($p);$b.Dispose()}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
C 1875 198 400; C 1875 198 400
foreach($x in 620,640,660,680,700,720){
  foreach($y in 44,50,56,62){
    C $x $y 350
    Shot "$OutDir\_tab_cal_${x}_${y}.png"
  }
}
Write-Host 'tab calibration done'

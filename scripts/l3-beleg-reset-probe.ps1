# Reset: Beende-Button + alle MDI schliessen, dann Probe
param([string]$OutDir = "$env:USERPROFILE\Pictures\L3-Capture-2026-08-22-dropdown-leaves")
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies System.Drawing @"
using System; using System.Runtime.InteropServices; using System.Drawing;
public class L3Rs {
  public delegate bool EP(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EP cb, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, System.Text.StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
  public static void Click(int x,int y){ SetCursorPos(x,y); mouse_event(2,0,0,0,UIntPtr.Zero); mouse_event(4,0,0,0,UIntPtr.Zero);} }
"@
$hwnd=[IntPtr]::Zero;$best=0
[L3Rs]::EnumWindows([L3Rs+EP]{param($h,$l)$sb=New-Object System.Text.StringBuilder 512;[L3Rs]::GetWindowText($h,$sb,512)|Out-Null;if($sb.ToString()-match '10\.200\.1\.3'){$r=New-Object L3Rs+RECT;[L3Rs]::GetWindowRect($h,[ref]$r)|Out-Null;$a=($r.R-$r.L)*($r.B-$r.T);if($a -gt $script:best){$script:best=$a;$script:hwnd=$h}};return $true},[IntPtr]::Zero)|Out-Null
$r=New-Object L3Rs+RECT;[L3Rs]::GetWindowRect($hwnd,[ref]$r)|Out-Null; $ox=$r.L;$oy=$r.T
function C($x,$y,$ms=350){[L3Rs]::Click($ox+$x,$oy+$y);Start-Sleep -Milliseconds $ms}
function Shot($p){$rr=New-Object L3Rs+RECT;[L3Rs]::GetWindowRect($hwnd,[ref]$rr)|Out-Null;$w=$rr.R-$rr.L;$h=$rr.B-$rr.T;$b=New-Object Drawing.Bitmap $w,$h;$g=[Drawing.Graphics]::FromImage($b);$g.CopyFromScreen($rr.L,$rr.T,0,0,[Drawing.Size]::new($w,$h));$g.Dispose();$b.Save($p);$b.Dispose()}

Shot "$OutDir\_before_reset.png"
# Beende (unten rechts), MDI-X, FENSTER Alle Fenster
C 1845 985 500
C 1875 198 400
C 900 58 250
C 520 108 600
Shot "$OutDir\_after_reset.png"
C 660 58 250
C 215 108 550
Shot "$OutDir\_beleg_menu_after_reset.png"
Write-Host 'reset probe done'

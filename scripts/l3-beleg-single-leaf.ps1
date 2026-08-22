# Einzel-Leaf: Tab AW -> Beleg-Icon -> Menü-Zeile per Maus (kein SendKeys)
param(
  [int]$LeafIndex = 0,
  [string]$LeafName = 'unerledigte_bestellungen',
  [int]$MenuY = 133,
  [string]$OutDir = "$env:USERPROFILE\Pictures\L3-Capture-2026-08-22-dropdown-leaves"
)
$ErrorActionPreference='Stop'
Add-Type -ReferencedAssemblies System.Drawing @"
using System; using System.Runtime.InteropServices; using System.Drawing; using System.Drawing.Imaging;
public class L1 { public delegate bool EP(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EP cb, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, System.Text.StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int X, int Y, int W, int H, bool r);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
  public static void Click(int x,int y){ SetCursorPos(x,y); mouse_event(2,0,0,0,UIntPtr.Zero); mouse_event(4,0,0,0,UIntPtr.Zero);} }
"@
Add-Type -AssemblyName System.Windows.Forms
$hwnd=[IntPtr]::Zero;$a0=0
[L1]::EnumWindows([L1+EP]{param($h,$l)$sb=New-Object System.Text.StringBuilder 512;[L1]::GetWindowText($h,$sb,512)|Out-Null;if($sb.ToString()-match '10\.200\.1\.3'){$r=New-Object L1+RECT;[L1]::GetWindowRect($h,[ref]$r)|Out-Null;$aa=($r.R-$r.L)*($r.B-$r.T);if($aa -gt $script:a0){$script:a0=$aa;$script:hwnd=$h}};return $true},[IntPtr]::Zero)|Out-Null
$s=[Windows.Forms.Screen]::PrimaryScreen.Bounds
[L1]::MoveWindow($hwnd,-8,-8,$s.Width+16,$s.Height+16,$true)|Out-Null
[L1]::SetForegroundWindow($hwnd)|Out-Null; Start-Sleep 800
$r=New-Object L1+RECT;[L1]::GetWindowRect($hwnd,[ref]$r)|Out-Null; $ox=$r.L;$oy=$r.T
function Shot($p){$rr=New-Object L1+RECT;[L1]::GetWindowRect($hwnd,[ref]$rr)|Out-Null;$w=$rr.R-$rr.L;$h=$rr.B-$rr.T;$b=New-Object Drawing.Bitmap $w,$h;$g=[Drawing.Graphics]::FromImage($b);$g.CopyFromScreen($rr.L,$rr.T,0,0,[Drawing.Size]::new($w,$h));$g.Dispose();$b.Save($p,[Drawing.Imaging.ImageFormat]::Png);$b.Dispose()}
function C($x,$y,$ms=400){[L1]::Click($ox+$x,$oy+$y);Start-Sleep -Milliseconds $ms}
C 660 58 300; C 660 58 200; Shot "$OutDir\_tab_aw.png"
C 215 108 550; Shot "$OutDir\_beleg_menu_tmp.png"
$y = $MenuY + ($LeafIndex * 22)
C 215 $y 1800
Shot "$OutDir\beleg_leaf_${LeafIndex}_${LeafName}.png"
Write-Host "saved leaf $LeafIndex y=$y"

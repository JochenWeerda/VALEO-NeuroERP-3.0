# Nur Beleg-Kontrolle Leaves (bewaehrtes RdpLeaf-Muster)
param([string]$OutDir = "$env:USERPROFILE\Pictures\L3-Capture-2026-08-22-dropdown-leaves")
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
  [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  public const uint MOUSE_LEFTDOWN = 0x0002; public const uint MOUSE_LEFTUP = 0x0004;
  public static void LeftClick(int x,int y){ SetCursorPos(x,y); mouse_event(MOUSE_LEFTDOWN,0,0,0,UIntPtr.Zero); mouse_event(MOUSE_LEFTUP,0,0,0,UIntPtr.Zero); }
}
"@
Add-Type -AssemblyName System.Windows.Forms
$hwnd=[IntPtr]::Zero;$a0=0
[RdpLeaf]::EnumWindows([RdpLeaf+EnumWindowsProc]{param($h,$l)$sb=New-Object System.Text.StringBuilder 512;[RdpLeaf]::GetWindowText($h,$sb,512)|Out-Null;if($sb.ToString()-match '10\.200\.1\.3'){$r=New-Object RdpLeaf+RECT;[RdpLeaf]::GetWindowRect($h,[ref]$r)|Out-Null;$aa=($r.Right-$r.Left)*($r.Bottom-$r.Top);if($aa -gt $script:a0){$script:a0=$aa;$script:hwnd=$h}};return $true},[IntPtr]::Zero)|Out-Null
[RdpLeaf]::ShowWindow($hwnd,3)|Out-Null
$scr=[Windows.Forms.Screen]::PrimaryScreen.Bounds
[RdpLeaf]::MoveWindow($hwnd,-8,-8,$scr.Width+16,$scr.Height+16,$true)|Out-Null
[RdpLeaf]::SetForegroundWindow($hwnd)|Out-Null; Start-Sleep 800
$r=New-Object RdpLeaf+RECT;[RdpLeaf]::GetWindowRect($hwnd,[ref]$r)|Out-Null
$o=@{X=$r.Left;Y=$r.Top;W=$r.Right-$r.Left;H=$r.Bottom-$r.Top}
function Shot($p){[RdpLeaf]::SetForegroundWindow($hwnd)|Out-Null;Start-Sleep 150;$rr=New-Object RdpLeaf+RECT;[RdpLeaf]::GetWindowRect($hwnd,[ref]$rr)|Out-Null;$w=$rr.Right-$rr.Left;$h=$rr.Bottom-$rr.Top;$b=New-Object Drawing.Bitmap $w,$h;$g=[Drawing.Graphics]::FromImage($b);$g.CopyFromScreen($rr.Left,$rr.Top,0,0,[Drawing.Size]::new($w,$h));$g.Dispose();$b.Save($p,[Drawing.Imaging.ImageFormat]::Png);$b.Dispose()}
function C($x,$y,$ms=800){[RdpLeaf]::LeftClick($o.X+$x,$o.Y+$y);Start-Sleep -Milliseconds $ms}
function Close-Mdi{1..5|%{[Windows.Forms.SendKeys]::SendWait('{ESC}');Start-Sleep 100;[Windows.Forms.SendKeys]::SendWait('^{F4}');Start-Sleep 200}}
function Open-BelegMenu{C 660 58 350;C 660 58 250;C 215 108 550}
$leaves=@('unerledigte_bestellungen','eingangsls_kontrolle','auftrags_kontrolle','lieferschein_kontrolle','gesperrte_ls','nicht_fakturierte')
New-Item -ItemType Directory -Force -Path $OutDir|Out-Null
$log=Join-Path $OutDir 'beleg-only-log.txt'
"start $(Get-Date -Format o) size=$($o.W)x$($o.H)"|Set-Content $log
Close-Mdi
Open-BelegMenu; Shot "$OutDir\beleg_menu_open_final.png"
$i=0; foreach($leaf in $leaves){
  Open-BelegMenu
  $y=133+$i*22
  C 175 $y 1800
  Shot "$OutDir\beleg_leaf_final_${i}_${leaf}.png"
  "ok $i $leaf y=$y"|Add-Content $log
  Close-Mdi; $i++
}
"end $(Get-Date -Format o)"|Add-Content $log
Write-Host 'beleg-only done'

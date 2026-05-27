; VALEO NeuroERP — WhisperBar AutoHotkey v1.1 (Windows)
; Strg+Shift+1: ERP-Fenster aktivieren + Browser-Diktat-Shortcut
; Strg+Shift+2: Clipboard-Summary via PowerShell + ki-usability-api
;
; Installation: AutoHotkey v1.1+ installieren, Skript doppelklicken oder Autostart.

#SingleInstance Force
#NoEnv
SetTitleMatchMode, 2

ERP_TITLE := "VALEO"
SCRIPT_DIR := A_ScriptDir

^+1::
    IfWinExist, %ERP_TITLE%
    {
        WinActivate
        Sleep, 150
        Send, ^+1
    }
    else
    {
        ToolTip, VALEO NeuroERP Fenster nicht gefunden
        SetTimer, ClearTip, -2000
    }
return

^+2::
    ps1 := SCRIPT_DIR . "\whisperbar-summary.ps1"
    IfNotExist, %ps1%
    {
        ToolTip, whisperbar-summary.ps1 nicht gefunden
        SetTimer, ClearTip, -2000
        return
    }
    RunWait, powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ps1%", , Hide
    if (ErrorLevel = 0)
    {
        ToolTip, Zusammenfassung in Zwischenablage
    }
    else
    {
        ToolTip, Summary fehlgeschlagen (ki-usability laeuft?)
    }
    SetTimer, ClearTip, -2500
return

ClearTip:
    ToolTip
return

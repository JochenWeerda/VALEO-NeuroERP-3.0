$domains = Get-ChildItem packages -Directory
foreach ($domain in $domains) {
    Write-Host "Checking $domain"
    $result = cmd /c "cd $($domain.FullName) && npm run lint 2>&1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "$domain has lint errors"
        # output first few lines
        $result | Select-Object -First 5
    } else {
        Write-Host "$domain is clean"
    }
}
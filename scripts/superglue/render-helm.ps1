$tempChart = Join-Path $env:TEMP ("superglue-chart-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempChart | Out-Null
Copy-Item -Recurse -Path "k8s/helm/valeo-erp/*" -Destination $tempChart
try {
    $renderPath = "$env:TEMP\\superglue-helm-render.yaml"
    if (Get-Command helm -ErrorAction SilentlyContinue) {
        helm dependency build $tempChart | Out-Null
        helm template superglue $tempChart `
          --set superglue.enabled=true `
          --set superglue.ingress.enabled=true `
          --set superglue.backup.enabled=true `
          | Set-Content -Path $renderPath
    } else {
        docker run --rm `
          -v "${tempChart}:/chart" `
          -v "${env:TEMP}:/tmp" `
          alpine/helm:3.17.2 `
          sh -lc "helm dependency build /chart >/dev/null && helm template superglue /chart --set superglue.enabled=true --set superglue.ingress.enabled=true --set superglue.backup.enabled=true >/tmp/superglue-helm-render.yaml"
    }

    if (-not (Test-Path $renderPath)) { throw "helm render file missing" }
    if ((Get-Item $renderPath).Length -le 0) { throw "helm render file empty" }
    Write-Host "helm render ok"
}
finally {
    Remove-Item -Recurse -Force $tempChart
}

param(
    [Parameter(Mandatory = $true)]
    [string]$Root
)

$ErrorActionPreference = "Stop"

$rootPath = (Resolve-Path -LiteralPath $Root).Path
$serviceXmlPath = Join-Path $rootPath "PredictionMarketBotService.xml"
$waitressPath = Join-Path $rootPath ".venv\Scripts\waitress-serve.exe"
$logPath = Join-Path $rootPath "logs"

$content = @"
<service>
  <id>PredictionMarketBot</id>
  <name>Prediction Market Bot Server</name>
  <description>Runs the Prediction Market Bot backend server.</description>

  <workingdirectory>$rootPath</workingdirectory>
  <executable>$waitressPath</executable>
  <arguments>--listen=127.0.0.1:5050 src.web_app:app</arguments>

  <env name="PYTHONUNBUFFERED" value="1" />

  <logpath>$logPath</logpath>
  <log mode="roll-by-size">
    <sizeThreshold>10485760</sizeThreshold>
    <keepFiles>5</keepFiles>
  </log>

  <onfailure action="restart" delay="5 sec" />
  <onfailure action="restart" delay="30 sec" />
</service>
"@

Set-Content -LiteralPath $serviceXmlPath -Value $content -Encoding UTF8
[xml](Get-Content -LiteralPath $serviceXmlPath -Raw) | Out-Null
Write-Host "Wrote $serviceXmlPath"

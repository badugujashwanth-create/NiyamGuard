[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$BaseUrl,
  [string]$FfmpegPath = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$frontendDir = Join-Path $repoRoot "frontend"
$demoDir = Join-Path $repoRoot "docs\demo"
$verificationDir = Join-Path $demoDir "verification"
[IO.Directory]::CreateDirectory($verificationDir) | Out-Null

function Resolve-Ffmpeg {
  param([string]$RequestedPath)
  if ($RequestedPath) { return (Resolve-Path $RequestedPath).Path }
  if ($env:NIYAMGUARD_FFMPEG) { return (Resolve-Path $env:NIYAMGUARD_FFMPEG).Path }
  $installed = Get-Command ffmpeg -ErrorAction SilentlyContinue
  if ($null -ne $installed) { return $installed.Source }
  $cached = Get-ChildItem (Join-Path $env:TEMP "nira-ffmpeg-8.1.2") -Recurse -Filter ffmpeg.exe -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($null -ne $cached) { return $cached.FullName }
  throw "FFmpeg is required. Pass -FfmpegPath or set NIYAMGUARD_FFMPEG."
}

function New-Narration {
  param([string]$OutputPath)
  Add-Type -AssemblyName System.Speech
  $paragraphs = (Get-Content -Raw -Encoding utf8 (Join-Path $demoDir "NARRATION.md")) -split "(?:\r?\n){2,}" |
    Where-Object { $_ -and $_ -notmatch '^#' } |
    ForEach-Object { ($_ -replace '[`*_#]', '').Trim() }
  $builder = New-Object System.Speech.Synthesis.PromptBuilder
  foreach ($paragraph in $paragraphs) {
    $builder.AppendText($paragraph)
    $builder.AppendBreak([TimeSpan]::FromSeconds(3))
  }
  $voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
  try {
    $voice.Rate = -1
    $voice.Volume = 90
    $voice.SetOutputToWaveFile($OutputPath)
    $voice.Speak($builder)
  }
  finally { $voice.Dispose() }
}

$ffmpeg = Resolve-Ffmpeg $FfmpegPath
$ffprobe = Join-Path (Split-Path -Parent $ffmpeg) "ffprobe.exe"
if (-not (Test-Path -LiteralPath $ffprobe)) { throw "ffprobe.exe was not found beside FFmpeg." }

$health = Invoke-WebRequest -Uri $BaseUrl -UseBasicParsing -TimeoutSec 10
if ($health.StatusCode -ne 200) { throw "The frontend is not healthy at $BaseUrl." }

$env:DEMO_BASE_URL = $BaseUrl.TrimEnd('/')
Push-Location $frontendDir
try {
  npm exec playwright test tests/e2e/product-walkthrough.spec.ts -- --workers=1
  if ($LASTEXITCODE -ne 0) { throw "The complete product simulation failed." }
}
finally { Pop-Location }

$sourceVideo = Get-ChildItem -Path (Join-Path $frontendDir "test-results") -Filter "*.webm" -Recurse |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
if ($null -eq $sourceVideo) { throw "Playwright completed without producing a WebM video." }

$runId = [guid]::NewGuid().ToString("N")
$workDir = Join-Path $env:TEMP "niyamguard-video-$runId"
[IO.Directory]::CreateDirectory($workDir) | Out-Null
$narration = Join-Path $workDir "narration.wav"
$output = Join-Path $demoDir "demo.webm"
New-Narration $narration

$sourceProbe = (& $ffprobe -v error -show_entries "format=duration" -of json $sourceVideo.FullName) | Out-String | ConvertFrom-Json
$duration = [double]$sourceProbe.format.duration
if ($duration -lt 180) { throw "Recorded simulation is too short: $duration seconds." }

$audioFilter = "[1:a]apad=pad_dur=$duration[a]"
& $ffmpeg -hide_banner -loglevel warning -y -i $sourceVideo.FullName -i $narration `
  -filter_complex $audioFilter -map 0:v:0 -map "[a]" `
  -c:v libvpx-vp9 -crf 38 -b:v 0 -deadline realtime -cpu-used 8 -row-mt 1 `
  -c:a libopus -b:a 64k -t $duration $output
if ($LASTEXITCODE -ne 0) { throw "Final demo encoding failed." }

& $ffmpeg -hide_banner -loglevel error -y -ss 00:01:40 -i $output -frames:v 1 (Join-Path $demoDir "demo-thumbnail.png")
$frameTimes = @(
  "00:00:10",
  "00:00:35",
  "00:01:10",
  "00:02:20",
  "00:03:15",
  "00:04:00",
  "00:04:10",
  "00:04:20",
  "00:04:28",
  "00:04:40",
  "00:05:05"
)
for ($index = 0; $index -lt $frameTimes.Count; $index++) {
  & $ffmpeg -hide_banner -loglevel error -y -ss $frameTimes[$index] -i $output -frames:v 1 `
    (Join-Path $verificationDir ("{0:D2}-frame.png" -f ($index + 1)))
}

$probeJson = (& $ffprobe -v error -show_entries "format=duration,size:stream=codec_type,codec_name,width,height" -of json $output) | Out-String
$probe = $probeJson | ConvertFrom-Json
$videoStream = $probe.streams | Where-Object { $_.codec_type -eq "video" } | Select-Object -First 1
$audioStream = $probe.streams | Where-Object { $_.codec_type -eq "audio" } | Select-Object -First 1
if ([double]$probe.format.duration -lt 180 -or $videoStream.width -ne 1280 -or $videoStream.height -ne 720 -or $null -eq $audioStream) {
  throw "Demo acceptance failed."
}
$evidence = [ordered]@{
  generated_at_utc = [DateTime]::UtcNow.ToString("o")
  duration_seconds = [Math]::Round([double]$probe.format.duration, 3)
  width = $videoStream.width
  height = $videoStream.height
  video_codec = $videoStream.codec_name
  audio_codec = $audioStream.codec_name
  captions = "demo-captions.vtt"
  sha256 = (Get-FileHash -Algorithm SHA256 $output).Hash.ToLower()
  bytes = (Get-Item $output).Length
  verification_frames = $frameTimes.Count
  frame_timestamps = $frameTimes
}
[IO.File]::WriteAllText(
  (Join-Path $verificationDir "verification.json"),
  ($evidence | ConvertTo-Json) + [Environment]::NewLine,
  [Text.UTF8Encoding]::new($false)
)
$evidence | ConvertTo-Json

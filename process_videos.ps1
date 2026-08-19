$ErrorActionPreference = 'Stop'

$outputDir = 'D:\research\video\01'
$workDir = 'D:\english\01\video-work'
$apiUrl = 'https://transcribe.charithharshana.com/v1/transcriptions'
$videos = @(
    @{ Id = 'GUZauFzCyG0'; Url = 'https://www.youtube.com/watch?v=GUZauFzCyG0&list=PLIhruWRzLZ1g' },
    @{ Id = 'M5yynmc3czU'; Url = 'https://youtu.be/M5yynmc3czU?si=nKmfYKy1sG9fF8kU' },
    @{ Id = 'xWev5kaQLFQ'; Url = 'https://youtu.be/xWev5kaQLFQ?si=Gx17-F6N189axTaY' },
    @{ Id = 'NU7BbcvyDVI'; Url = 'https://youtu.be/NU7BbcvyDVI?si=PCl30xftNeN7oXgd' },
    @{ Id = 'uaOW0ep166c'; Url = 'https://youtu.be/uaOW0ep166c?si=ZAohpu__2Iaz60yK' },
    @{ Id = 'E3iowXKrqs4'; Url = 'https://youtu.be/E3iowXKrqs4?si=9DUIBlxP_s4cx1-q' },
    @{ Id = 'iyZpzg_wXLc'; Url = 'https://youtu.be/iyZpzg_wXLc?si=k86EkmYjmztbahAn' },
    @{ Id = 'PAp_OQphvj8'; Url = 'https://youtu.be/PAp_OQphvj8?si=zK9EK3GObOpOfrcj' },
    @{ Id = 'hFIkKBvH7po'; Url = 'https://youtu.be/hFIkKBvH7po?si=yDl4C_YHjxJdxfJa' },
    @{ Id = '12Ylx0mMT4s'; Url = 'https://youtu.be/12Ylx0mMT4s?si=c-6GI9pbw0AeItIQ' },
    @{ Id = '4GMD4MIyHtE'; Url = 'https://youtu.be/4GMD4MIyHtE?si=wWwvL6PaVFs1Hy8i' },
    @{ Id = 'cOxCE9VoW8M'; Url = 'https://youtu.be/cOxCE9VoW8M?si=ss4yIVp-ksKf9Vp4' },
    @{ Id = 'qwagr-XMHhs'; Url = 'https://youtu.be/qwagr-XMHhs?si=Y2TU60BWgaYw0_Wf' }
)

New-Item -ItemType Directory -Force -Path $workDir | Out-Null
$envLines = Get-Content -LiteralPath 'D:\english\01\.env'
$keyLine = $envLines | Where-Object { $_ -match '^FASTWHISPER_API_KEY=' } | Select-Object -First 1
if (-not $keyLine) { throw 'FASTWHISPER_API_KEY is missing from .env' }
$apiKey = $keyLine.Substring('FASTWHISPER_API_KEY='.Length)
if ([string]::IsNullOrWhiteSpace($apiKey)) { throw 'FASTWHISPER_API_KEY is empty' }

function Invoke-YtDlpJson([string]$url) {
    $json = & yt-dlp --no-warnings --skip-download --dump-single-json --no-playlist --extractor-args 'youtube:player_client=android' $url 2>$null
    if ($LASTEXITCODE -ne 0) { throw "yt-dlp metadata failed for $url" }
    return ($json -join "`n") | ConvertFrom-Json
}

function Format-Time([double]$seconds) {
    $span = [TimeSpan]::FromSeconds($seconds)
    if ($span.Hours -gt 0) { return $span.ToString('hh\:mm\:ss') }
    return $span.ToString('mm\:ss')
}

function Escape-Markdown([string]$value) {
    if ($null -eq $value) { return '' }
    return $value.Trim()
}

$results = @()
for ($i = 0; $i -lt $videos.Count; $i++) {
    $video = $videos[$i]
    $number = '{0:D2}' -f ($i + 1)
    Write-Host "[$number/13] Retrieving metadata and audio for $($video.Id)"
    try {
        $meta = Invoke-YtDlpJson $video.Url
        $audio = Join-Path $workDir "$($video.Id).mp3"
        if (-not (Test-Path -LiteralPath $audio)) {
            & yt-dlp --no-warnings --no-playlist --extractor-args 'youtube:player_client=android' -f '18/bestaudio/best' -x --audio-format mp3 --audio-quality 0 -o $audio $video.Url 2>$null
            if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $audio)) { throw 'audio download failed' }
        }

        Write-Host "[$number/13] Transcribing $($video.Id)"
        $transcriptionPath = Join-Path $workDir "$($video.Id).json"
        if (-not (Test-Path -LiteralPath $transcriptionPath)) {
            $form = @{
                model = 'sinhala'
                language = 'si'
                initial_prompt = 'Sinhala, English, Comprehensible Input, Learner-Centered Pedagogy, Cognitive Load Theory, Cornell Note Method, microlearning, Motivation Theory, Cognitive Behavioral Therapy, CBT, active learning, spaced repetition, retrieval practice, practice testing, planning, journaling, goals, productivity, procrastination, exam, study, learning'
                vad_filter = 'true'
                min_silence_duration_ms = '1000'
                response_format = 'verbose_json'
                timestamp_granularities = 'segment'
            }
            $curlArgs = @(
                '-sS', '--max-time', '3600', '-X', 'POST', $apiUrl,
                '-H', "Authorization: Bearer $apiKey",
                '-F', "file=@$audio",
                '-F', 'model=sinhala',
                '-F', 'language=si',
                '-F', "initial_prompt=$($form.initial_prompt)",
                '-F', 'vad_filter=true',
                '-F', 'min_silence_duration_ms=1000',
                '-F', 'response_format=verbose_json',
                '-F', 'timestamp_granularities=segment'
            )
            $responseJson = & curl.exe @curlArgs
            if ($LASTEXITCODE -ne 0) { throw "transcription API request failed for $($video.Id)" }
            $responseJson -join "`n" | Set-Content -LiteralPath $transcriptionPath -Encoding UTF8
        }
        $tx = Get-Content -LiteralPath $transcriptionPath -Raw | ConvertFrom-Json

        $segments = @($tx.segments)
        $transcript = ($segments | ForEach-Object {
            $start = Format-Time ([double]$_.start)
            $text = ([string]$_.text).Trim()
            if ($text) { "[$start] $text" }
        }) -join "`n"
        if (-not $transcript) { $transcript = ([string]$tx.text).Trim() }
        if (-not $transcript) { $transcript = '[No transcript text returned by the transcription API]' }

        $summary = if ($meta.description) { (($meta.description -split "`n")[0]).Trim() } else { 'No summary was available from the video metadata.' }
        $quality = "Audio transcription via FastWhisperAPI v1.2.0 using the Sinhala model with language=si and timestamped segments. Captions supplied by YouTube were absent or unreliable for this video, so they were not used as the transcript source. API detected language: $($tx.detected_language); language probability: $($tx.language_probability)."
        if ($tx.detected_language -ne 'si') { $quality += ' The detected language differs from the requested Sinhala language; review English/code-switched portions.' }

        $markdown = @"
# $($meta.title)

- **Video URL:** $($video.Url)
- **Video ID:** $($video.Id)
- **Channel:** $($meta.uploader)
- **Publication date:** $($meta.upload_date)
- **Duration:** $(Format-Time ([double]$meta.duration))
- **Views at retrieval:** $($meta.view_count)
- **Likes at retrieval:** $($meta.like_count)

## Description

$(Escape-Markdown ([string]$meta.description))

## Brief Summary

$summary

## Complete Transcript

$transcript

## Transcript Source and Quality

$quality

Technical terms and proper names are preserved where the model recognized them. Some English code-switches may appear as Sinhala phonetic spellings because the Sinhala model is optimized for Sinhala-script speech. Music, silence, and unintelligible audio are omitted by the transcription service where applicable. No API credentials are included in this report.
"@
        Set-Content -LiteralPath (Join-Path $outputDir "$number.md") -Value $markdown -Encoding UTF8
        $results += [pscustomobject]@{ Number = $number; Id = $video.Id; Status = 'success'; TranscriptChars = $transcript.Length }
    } catch {
        $errorText = $_.Exception.Message
        $markdown = @"
# Video ${number}: processing failed

- **Video URL:** $($video.Url)
- **Video ID:** $($video.Id)

## Failure

$errorText

Metadata or transcript retrieval did not complete for this video. No API credentials were included in this report.
"@
        Set-Content -LiteralPath (Join-Path $outputDir "$number.md") -Value $markdown -Encoding UTF8
        $results += [pscustomobject]@{ Number = $number; Id = $video.Id; Status = "failed: $errorText"; TranscriptChars = 0 }
        Write-Warning "[$number/13] $errorText"
    }
}

$results | ConvertTo-Json -Compress

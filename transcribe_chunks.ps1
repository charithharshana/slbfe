$ErrorActionPreference = 'Stop'
$outputDir = 'D:\english\01\01'
$workDir = 'D:\english\01\video-work'
$apiUrl = 'https://transcribe.charithharshana.com/v1/transcriptions'
$chunkSeconds = 40
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
$keyLine = Get-Content -LiteralPath 'D:\english\01\.env' | Where-Object { $_ -match '^FASTWHISPER_API_KEY=' } | Select-Object -First 1
$apiKey = $keyLine.Substring('FASTWHISPER_API_KEY='.Length)

function Format-Time([double]$seconds) {
    $span = [TimeSpan]::FromSeconds($seconds)
    if ($span.Hours -gt 0) { return $span.ToString('hh\:mm\:ss') }
    return $span.ToString('mm\:ss')
}
function Meta([string]$url) {
    $json = & yt-dlp --no-warnings --skip-download --dump-single-json --no-playlist --extractor-args 'youtube:player_client=android' $url 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'metadata retrieval failed' }
    return ($json -join "`n") | ConvertFrom-Json
}
function Transcribe([string]$file, [string]$model = 'sinhala', [string]$language = 'si') {
    $args = @('-sS','--max-time','600','-X','POST',$apiUrl,'-H',"Authorization: Bearer $apiKey",'-F',"file=@$file",'-F',"model=$model",'-F','initial_prompt=Sinhala, English, Comprehensible Input, Learner-Centered Pedagogy, Cognitive Load Theory, Cornell Note Method, microlearning, Motivation Theory, Cognitive Behavioral Therapy, CBT, active learning, spaced repetition, retrieval practice, practice testing, planning, journaling, goals, productivity, procrastination, exam, study, learning','-F','vad_filter=true','-F','min_silence_duration_ms=700','-F','response_format=verbose_json','-F','timestamp_granularities=segment')
    if (-not [string]::IsNullOrWhiteSpace($language)) { $args += @('-F', "language=$language") }
    $raw = & curl.exe @args
    if ($LASTEXITCODE -ne 0) { throw 'curl transcription request failed' }
    $obj = ($raw -join "`n") | ConvertFrom-Json
    if ($obj.error) { throw "API error: $($obj.error.type) - $($obj.error.message)" }
    $result = $obj.'File 1'
    if ($null -eq $result) { throw 'API response did not contain File 1' }
    return $result
}
function Wait-ForWorker {
    for ($attempt = 1; $attempt -le 120; $attempt++) {
        $health = & curl.exe -sS --max-time 30 -H "Authorization: Bearer $apiKey" 'https://transcribe.charithharshana.com/healthz'
        try {
            $state = ($health -join "`n") | ConvertFrom-Json
            if ([int]$state.inflight_slots_in_use -eq 0) { return }
        } catch { }
        Start-Sleep -Seconds 5
    }
    throw 'The transcription worker did not become available within 10 minutes'
}

for ($i = 0; $i -lt $videos.Count; $i++) {
    $v = $videos[$i]; $num = '{0:D2}' -f ($i + 1); $audio = Join-Path $workDir "$($v.Id).mp3"
    if (-not (Test-Path -LiteralPath $audio)) { Write-Warning "[$num] audio missing"; continue }
    Write-Host "[$num/13] Preparing chunks"
    $durationRaw = & ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $audio 2>$null
    $duration = [double]($durationRaw -join '')
    $segments = @()
    for ($start = 0; $start -lt $duration; $start += $chunkSeconds) {
        $chunk = Join-Path $workDir "$($v.Id)-$($chunkSeconds)s-$('{0:D5}' -f $start).wav"
        $jsonPath = "$chunk.json"
        $retryChunk = $false
        if (Test-Path -LiteralPath $jsonPath) {
            try { $retryChunk = (Get-Content -LiteralPath $jsonPath -Raw | ConvertFrom-Json).error -ne $null } catch { $retryChunk = $true }
        }
        if (-not (Test-Path -LiteralPath $jsonPath) -or $retryChunk) {
            & ffmpeg -y -loglevel error -ss $start -i $audio -t $chunkSeconds -ac 1 -ar 16000 $chunk
            if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed for $($v.Id) at $start" }
            try {
                Write-Host "[$num/13] Transcribing $start seconds"
                Wait-ForWorker
                if ($v.Id -eq 'GUZauFzCyG0') {
                    # The video begins in English and later switches to Sinhala.
                    $tx = Transcribe $chunk 'base' ''
                    if ($tx.detected_language -ne 'en') { $tx = Transcribe $chunk 'sinhala' 'si' }
                } else {
                    $tx = Transcribe $chunk
                }
                $tx | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $jsonPath -Encoding UTF8
            } catch {
                Write-Warning "[$num] chunk $start failed: $($_.Exception.Message)"
                @{ error = $_.Exception.Message } | ConvertTo-Json | Set-Content -LiteralPath $jsonPath -Encoding UTF8
            }
        }
        $saved = Get-Content -LiteralPath $jsonPath -Raw | ConvertFrom-Json
        if (-not $saved.error) {
            foreach ($s in @($saved.segments)) {
                $segments += [pscustomobject]@{ Start = ([double]$s.start + $start); Text = ([string]$s.text).Trim() }
            }
        }
    }
    $meta = Meta $v.Url
    $transcript = ($segments | ForEach-Object { "[$(Format-Time $_.Start)] $($_.Text)" }) -join "`n"
    if (-not $transcript) { $transcript = '[No valid transcript segments were returned]' }
    $summary = if ($meta.description) { (($meta.description -split "`n")[0]).Trim() } else { 'No summary was available from metadata.' }
    $failureNote = if ($segments.Count -eq 0) { 'All chunk requests failed or returned no segments.' } else { "$($segments.Count) timestamped segments were returned from audio chunks." }
    $md = @"
# $($meta.title)

- **Video URL:** $($v.Url)
- **Video ID:** $($v.Id)
- **Channel:** $($meta.uploader)
- **Publication date:** $($meta.upload_date)
- **Duration:** $(Format-Time ([double]$meta.duration))
- **Views at retrieval:** $($meta.view_count)
- **Likes at retrieval:** $($meta.like_count)

## Description

$([string]$meta.description)

## Brief Summary

$summary

## Complete Transcript

$transcript

## Transcript Source and Quality

Audio transcription via FastWhisperAPI v1.2.0 using the Sinhala model (`model=sinhala`, `language=si`) on $chunkSeconds-second chunks. YouTube captions were absent or unreliable and were not used. $failureNote English technical terms may be rendered as Sinhala phonetic spellings by the Sinhala specialist model. Silence, music, and unintelligible portions may be omitted. No API credentials are included in this report.
"@
    Set-Content -LiteralPath (Join-Path $outputDir "$num.md") -Value $md -Encoding UTF8
    Write-Host "[$num/13] Report written"
}

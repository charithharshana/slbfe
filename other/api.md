# API Documentation

Base URL (public): `https://transcribe.charithharshana.com`

Local URL (server): `http://95.216.121.130:8000`

Current API version: **1.2.0**

- 1.1.0 — Whisper + Kokoro TTS
- 1.2.0 — adds optional Sinhala (`si`) transcription via the `model=sinhala` alias. Fully backward compatible with 1.x.

---

## What's new in 1.2.0

- New `model` value `sinhala` routes requests to a fine-tuned Whisper model (`Lingalingeswaran/whisper-small-sinhala`) running through CTranslate2 for fast inference.
- New fields on `GET /info`: `sinhala_model`, `sinhala_ready`.
- New guidance for **Singlish** (Sinhala-script audio that mixes Sinhala with English technical terms like "terminal", "Git", "PowerShell", "install").

The default English workflow is **unchanged**:

- `model=base` / `small` / `large-v3` / ... keep using the openai-whisper CTranslate2 weights exactly as before.
- `/v1/audio/speech` (Kokoro) is untouched.
- `/info` response shape gains two optional fields; existing clients that don't read them keep working.

---

## Authentication

All endpoints require API key authentication:

```http
Authorization: Bearer <FASTWHISPER_API_KEY>
```

API key source:

- Required variable: `FASTWHISPER_API_KEY`
- Loaded from repo root `.env` file (or process environment)
- There is no default fallback key

If missing/invalid, response is:

- Status: `401`
- Body:

```json
{
  "error": {
    "message": "Incorrect API key",
    "type": "invalid_request_error",
    "param": "Authorization",
    "code": 401
  }
}
```

---

## Endpoints

### 1. GET `/`

- Description: Redirects to `/docs`.
- Auth required: Yes
- Response: HTTP `307` redirect

### 2. GET `/info`

- Description: Server/runtime info for Whisper + Kokoro + Sinhala capability.
- Auth required: Yes
- Response `200`:

```json
{
  "app": "FastWhisperAPI",
  "version": "1.2.0",
  "whisper_device": "cpu",
  "whisper_compute_type": "int8",
  "whisper_models": [
    "tiny.en", "tiny", "base.en", "base",
    "small.en", "small", "medium.en", "medium",
    "large-v1", "large-v2", "large-v3", "large",
    "distil-large-v2", "distil-medium.en",
    "distil-small.en", "distil-large-v3",
    "sinhala"
  ],
  "kokoro_enabled": true,
  "sinhala_model": "Lingalingeswaran/whisper-small-sinhala",
  "sinhala_ready": true
}
```

Field notes:

- `whisper_models` — every value accepted by the `model` form field on `POST /v1/transcriptions`. The new `sinhala` value is the alias that activates the Sinhala pipeline.
- `sinhala_model` — the Hugging Face repo id backing the alias.
- `sinhala_ready` — `true` when the converted CTranslate2 weights are present on disk and the endpoint will succeed; `false` when the conversion step has not been run on the deployment.

### 3. GET `/v1/voices`

- Description: Lists available Kokoro voices.
- Auth required: Yes
- Response `200`:

```json
{
  "object": "list",
  "data": [
    { "id": "af_heart", "object": "voice" },
    { "id": "bf_emma", "object": "voice" }
  ]
}
```

- Response `503` (Kokoro not configured):

```json
{
  "error": {
    "message": "Kokoro is not configured. Set KOKORO_MODEL_PATH and KOKORO_VOICES_PATH.",
    "type": "service_unavailable",
    "param": "kokoro",
    "code": 503
  }
}
```

### 4. POST `/v1/audio/speech` (Kokoro Integration)

- Description: Text-to-speech using Kokoro.
- Auth required: Yes
- Method: `POST`
- Content-Type: `application/json`

Request body:

```json
{
  "model": "kokoro",
  "input": "Read this text out loud.",
  "voice": "af_heart",
  "response_format": "wav",
  "speed": 1.0,
  "language": "en-us"
}
```

Field details:

- `model` (string): must be `kokoro` or `kokoro-82m`
- `input` (string): text to synthesize
- `voice` (string): voice id from `/v1/voices`
- `response_format` (string): currently `wav`
- `speed` (float): `0.5` to `2.0`
- `language` (string): one of `en-us`, `en-gb`, `fr-fr`, `ja`, `ko`, `zh`

Response:

- Status `200`
- Content-Type: `audio/wav`
- Binary WAV data
- Extra headers:
  - `X-Model: kokoro`
  - `X-Voice: <voice>`

Example curl:

```bash
curl -X POST "https://transcribe.charithharshana.com/v1/audio/speech" \
  -H "Authorization: Bearer <FASTWHISPER_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"model":"kokoro","input":"Hello from Kokoro.","voice":"af_heart","response_format":"wav","speed":1.0,"language":"en-us"}' \
  --output speech.wav
```

### 5. POST `/v1/transcriptions` (Whisper Integration)

- Description: Speech-to-text transcription using Faster-Whisper. Supports **English** (default) and **Sinhala** (`model=sinhala`).
- Auth required: Yes
- Method: `POST`
- Content-Type: `multipart/form-data`

Form fields:

| Field | Type | Default | Notes |
|---|---|---|---|
| `file` | one or more files | required | audio to transcribe |
| `model` | string | `base` | one of `whisper_models` from `/info`. Use `sinhala` for Sinhala. |
| `language` | ISO-639-1 | auto-detect | For Sinhala, pass `si`. |
| `initial_prompt` | string | empty | Strongly recommended for Sinhala to bias vocabulary toward technical English terms (see "Singlish" below). |
| `vad_filter` | boolean | `false` | Voice activity detection to skip silence. |
| `min_silence_duration_ms` | int | `1000` | VAD silence threshold. |
| `response_format` | enum | `text` | `text` or `verbose_json`. |
| `timestamp_granularities` | enum | `segment` | `segment` or `word`. Word-level is supported on both English and Sinhala. |

Successful response examples:

`response_format=text`:

```json
{ "File 1": { "text": "Transcribed text output" } }
```

`response_format=verbose_json`:

```json
{
  "File 1": {
    "filename": "sample.wav",
    "detected_language": "en",
    "language_probability": 0.99,
    "text": "Transcribed text output",
    "segments": [
      { "text": "Transcribed text output", "start": 0.0, "end": 2.3 }
    ]
  }
}
```

#### 5.1 English example (unchanged from 1.1.0)

```bash
curl -X POST "https://transcribe.charithharshana.com/v1/transcriptions" \
  -H "Authorization: Bearer <FASTWHISPER_API_KEY>" \
  -F "file=@sample.wav;type=audio/wav" \
  -F "model=base" \
  -F "response_format=verbose_json" \
  -F "timestamp_granularities=segment"
```

#### 5.2 Sinhala example (new in 1.2.0)

```bash
curl -X POST "https://transcribe.charithharshana.com/v1/transcriptions" \
  -H "Authorization: Bearer <FASTWHISPER_API_KEY>" \
  -F "file=@sinhala_lecture_01.mp3;type=audio/mpeg" \
  -F "model=sinhala" \
  -F "language=si" \
  -F "initial_prompt=Git, Bash, PowerShell, terminal, command prompt, install, Windows, Linux" \
  -F "response_format=verbose_json" \
  -F "timestamp_granularities=word"
```

Successful response (Sinhala, word-level):

```json
{
  "File 1": {
    "filename": "sinhala_lecture_01.mp3",
    "detected_language": "si",
    "language_probability": 1.0,
    "text": "ආයුබවන් මැට්පෝකොකොක් ස්ලාශ්කිල්ස් විෂයමාලාවේ පළමු පාඩම...",
    "segments": [
      {
        "text": "ආයුබවන් මැට්පෝකොකොක් ස්ලාශ්කිල්ස් විෂයමාලාවේ පළමු පාඩම වන",
        "start": 0.0,
        "end": 5.54,
        "words": [
          { "word": "ආයුබවන්",   "start": 0.00, "end": 1.06 },
          { "word": "මැට්පෝකොකොක්", "start": 1.06, "end": 2.40 }
        ]
      }
    ]
  }
}
```

---

## Singlish (Sinhala + technical English) — guidance

**The model.** `Lingalingeswaran/whisper-small-sinhala` is a Whisper-Small (244 M params) fine-tuned primarily on Sinhala Common Voice. It is excellent at Sinhala-script narration but its English vocabulary coverage is narrow: technical tokens like `terminal`, `Git`, `PowerShell`, `install`, `kernel`, `bash` are typically rendered as **Sinhala phonetic transliterations** (e.g. `ටර්මිනල්`, `ගිට්`, `පවර්ෂෙල්`, `ඉන්ස්ටෝල්`).

### Why this happens

| Cause | Effect |
|---|---|
| Training data skew | The model's decoder has a much larger prior for Sinhala script than for English ASCII. |
| Model size | Whisper-Small (244 M) has fewer spare capacity for code-switching than `large-v3` (1.5 B). |
| Acoustic similarity | Sinhala and English share many phonemes — short English tokens get pulled into Sinhala orthography. |
| Decoder confidence | Whisper tends to commit to one script per segment, so even a strong English phoneme can be forced into Sinhala. |

### Recommended practice (in priority order)

1. **Always set `language=si`** when calling `model=sinhala`. This stops the model from spending its first decode step on language-ID and concentrates capacity on transcription.
2. **Use `initial_prompt`** to bias the decoder toward the English vocabulary you expect. Whisper treats the prompt as a "previous segment", so the English terms are primed into the LM state. Recommended template:
   ```
   Git, Bash, PowerShell, terminal, command prompt, install, Windows, Linux, file, folder, repository, branch, commit, merge, kernel, drivers, debug
   ```
   Include only the terms relevant to the lecture. Overlong prompts waste decoder steps.
3. **Keep `beam_size=5`** (the API default) for mixed-language clips — beam search helps the model hold the English token until the audio is fully decoded.
4. **Don't combine `model=sinhala` with `language=en`**. The Sinhala weights are biased to Sinhala and produce garbled output on English-only audio.
5. **For pure English, use `model=base` or `large-v3`**. The Sinhala model should not be a default; it is a specialist.
6. **Word-level timestamps + per-word probability** (`timestamp_granularities=word`) lets the caller filter low-confidence tokens automatically (e.g. drop words with `probability < 0.5`).
7. **For audio with heavy code-switching**, prefer `model=large-v3` (English) for best fidelity, or split the audio manually and route each segment to the appropriate model. The 1.2.0 release does not auto-route.

### Quality expected on this PC (CPU, int8)

Measured against the bundled `sinhala\test\*.mp3` samples:

| File | Duration | Lang (p) | Segments | RTF |
|---|---|---|---|---|
| `0001-orientation-and-roadmap_si_vo_01.mp3` | 105.0 s | `si` 1.000 | 6 | 1.47× |
| `0001-orientation-and-roadmap_si_vo_02.mp3` | 132.1 s | `si` 1.000 | 11 | 2.13× |
| `0001-orientation-and-roadmap_si_vo_03.mp3` | 177.7 s | `si` 1.000 | 18 | 3.08× |

Per-word `language_probability=1.000` across every file confirms Sinhala-script detection is robust; English code-switches are the only weak spots and benefit most from the `initial_prompt` technique.

---

## Sinhala setup (one-time, per deployment)

`faster-whisper` only loads CTranslate2 weights (`model.bin`). The Hugging Face repo `Lingalingeswaran/whisper-small-sinhala` ships only transformers-format weights (`model.safetensors`). Convert once on each host:

```powershell
cd D:\Charith\development\FastWhisperAPI

# 1. install the conversion toolchain (only needed on the host that does conversion)
.\FastWhisperAPI-main\.venv\Scripts\pip.exe install torch --index-url https://download.pytorch.org/whl/cpu
.\FastWhisperAPI-main\.venv\Scripts\pip.exe install "transformers>=4.45" ctranslate2 tokenizers

# 2. convert (one-shot, ~460 MB download -> 236 MB int8 CTranslate2 dir)
$env:HF_HUB_DISABLE_SYMLINKS = "1"
.\FastWhisperAPI-main\.venv\Scripts\ct2-transformers-converter.exe `
    --model Lingalingeswaran/whisper-small-sinhala `
    --output_dir .\models\sinhala-ct2 `
    --quantization int8 --force
```

Resulting layout:

```
D:\Charith\development\FastWhisperAPI\models\sinhala-ct2\
  config.json
  vocabulary.json
  model.bin        (~236 MB)
```

### Configuration

| Env var | Default | Purpose |
|---|---|---|
| `SINHALA_MODEL_PATH` | `./models/sinhala-ct2` | Override the directory the loader reads from. Useful when the conversion lives on a separate drive or container path. |

The loader checks existence before constructing `WhisperModel`. If the path is missing, the request fails fast with:

```json
{
  "error": {
    "message": "Sinhala model not found at '...'. Set SINHALA_MODEL_PATH or convert the weights once with: ct2-transformers-converter --model Lingalingeswaran/whisper-small-sinhala --output_dir models/sinhala-ct2 --quantization int8",
    "type": "RuntimeError",
    "param": "model",
    "code": 500
  }
}
```

`/info` reports `sinhala_ready: false` until the conversion step has been completed.

### Verified deployment check

On 2026-08-19, `sinhala_short.wav` was transcribed through both the local origin and `https://transcribe.charithharshana.com` with `model=sinhala`, `language=si`, and `vad_filter=true`:

| Route | Status | Detected language | Result |
|---|---:|---|---|
| Local `http://127.0.0.1:8765` | `200` | `si` (1.0) | One segment, non-empty transcript |
| Public Cloudflare URL | `200` | `si` (1.0) | One segment, non-empty transcript |

This checks model loading, CPU inference, the API worker, authentication, the local origin, and the Cloudflare tunnel. It does not establish transcription quality for a different recording; verify quality against the source audio and use a relevant `initial_prompt` for technical vocabulary.

---

## CPU queue and timeout behavior

The default CPU deployment intentionally accepts one transcription at a time:

| Setting | Default | Meaning |
|---|---:|---|
| `MAX_INFLIGHT` | `1` | Maximum simultaneous transcriptions. |
| `INFLIGHT_QUEUE_TIMEOUT_S` | `5` | Maximum time a new request waits for the worker slot. |
| `REQUEST_TIMEOUT_S` | `90` | Inference budget before the API returns a timeout response. |

`GET /healthz` returns `inflight_slots_in_use`; send the same bearer token used for other API endpoints. A value of `0` means the worker is available.

Do not submit parallel requests to this CPU deployment. Wait for a request to finish before sending the next chunk. A `503` response means another transcription is still using the only worker slot; retry after the `Retry-After` response header, not by starting additional parallel retries.

The `90` second deadline is an API guard for Cloudflare-backed CPU inference. It is not evidence that model files are missing. Split long recordings into small sequential chunks and preserve their ordering in the client. A 90-second CPU chunk can exceed the request budget even when short audio works.

Timeout response:

```json
{
  "error": {
    "message": "Transcription exceeded the 90s request budget. Split CPU-transcribed audio into shorter chunks and retry.",
    "type": "timeout_error",
    "param": "file",
    "code": 504
  }
}
```

---

## Error Codes

- `400` Invalid request parameters (model/language/format/voice/etc.)
- `401` Missing or invalid API key
- `422` Validation errors (missing required fields)
- `500` Unexpected runtime errors (e.g. model or audio-decoding failure)
- `503` Transcription worker is busy; retry after the `Retry-After` header
- `504` Transcription exceeded `REQUEST_TIMEOUT_S`; split the audio and retry sequentially

---

## Troubleshooting

1. `401 Unauthorized` on all endpoints:
   - Confirm `FASTWHISPER_API_KEY` in container env matches client token.

2. `503` from `/v1/voices` or `/v1/audio/speech`:
   - Verify `KOKORO_MODEL_PATH` and `KOKORO_VOICES_PATH` point to existing files inside container (`C:\models\...`).

3. `503 Server is busy` from `/v1/transcriptions`:
   - A prior transcription is still using the single CPU worker slot.
   - Check `GET /healthz`; wait for `inflight_slots_in_use: 0`.
   - Respect `Retry-After` and send one retry only after that delay. Do not run concurrent retries.

4. `504 timeout_error` from `/v1/transcriptions`:
   - The request exceeded the CPU budget, typically because the audio chunk is too long.
   - Split the recording into shorter sequential chunks. Do not retry the same long chunk unchanged.
   - Keep `language=si` and use `vad_filter=true` for Sinhala recordings with silence.

5. Whisper transcription errors:
   - Confirm supported audio extension.
   - Check the active service logs for model download/runtime details. Docker logs only apply when Docker is the deployed origin:

   ```powershell
   docker logs speaches-windows --tail 200
   ```

6. Public endpoint not reachable:
   - Validate the origin listener used by the Cloudflare ingress rule.
   - For this host, `transcribe.charithharshana.com` routes to `127.0.0.1:8765`.
   - Confirm Cloudflare Tunnel service is running.

7. `500` on `model=sinhala` requests — model not found:
   - Check `GET /info` → `sinhala_ready` must be `true`.
   - Run the conversion step in the "Sinhala setup" section above.
   - Or set `SINHALA_MODEL_PATH` to a directory that already contains `model.bin`.

8. Sinhala transcripts look like Sinhala phonetic transliteration of English words:
   - You are hitting the Singlish case. Apply the guidance in "Singlish" above: set `language=si` and supply an `initial_prompt` with the English technical vocabulary expected in the audio.

9. Sinhala transcription is slow (>2× real-time):
   - CPU + int8 is the current deployment shape (RTF 1.5–3×). To go faster: install CUDA-enabled `torch`, set the env so `faster-whisper` selects `float16`, and re-run. RTF should drop to ~0.1×.

10. `HF_HUB_DISABLE_SYMLINKS` warning on Windows:
   - Non-fatal. Set the env var to `1` before any download to silence the warning and skip symlink creation (Windows requires admin / Developer Mode for symlinks).

---

## Backward compatibility matrix

| 1.1.0 client behavior | 1.2.0 server response | Compatible? |
|---|---|---|
| `POST /v1/transcriptions` with `model=base`, no `sinhala_*` field read | Same; `whisper_models` now also lists `"sinhala"` but the array remains a superset | yes |
| `GET /info` reads only existing fields | Existing fields unchanged in type and name; two additive nullable fields | yes |
| `POST /v1/audio/speech` (Kokoro) | Unchanged | yes |
| English default (`model=base`) | Hits the same cached `WhisperModel("base", ...)` because `lru_cache` keys on the argument | yes |
| New client wants `model=sinhala` | Routes to `models/sinhala-ct2`; raises 500 with a clear message if not converted yet | new capability |

No existing client request or response shape has been broken. All additive changes are designed so that 1.1.0 clients continue to operate against a 1.2.0 server with zero modifications.

---

## Rate Limiting

No built-in application rate limiting is enabled.

Recommended: enforce rate limits at Cloudflare (WAF/Rate Limiting) for `transcribe.charithharshana.com`.

Note for Sinhala: the first `model=sinhala` request in a process pays a one-time weight load (~1 s from local CT2, ~30–90 s if you point at the Hugging Face repo id instead of the local dir). Subsequent requests hit the `lru_cache` slot and add no startup cost.

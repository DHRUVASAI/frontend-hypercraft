# Voice-First UX & Indian Telephony Engineering (8 kHz PSTN to Low-Latency Turn-Taking)

## 1. Acoustic Physics of Indian Feature-Phone Telephony
Building for real feature phones (not clean studio microphones) requires designing for **8 kHz G.711 μ-law/A-law PSTN narrowband channels** (`300–3,400 Hz` passband):
- High-frequency fricatives & sibilants (`s`, `sh`, `f`, `th` above `4 kHz`) are clipped by PSTN filters, and retroflex vs. dental consonants in Telugu/Hindi degrade heavily under tractor/traffic noise (`SNR < 5 dB`).
- **Model Selection:** Benchmark against **AI4Bharat IndicVoices / IndicASR** (covering all 22 scheduled Indian languages with real rural dialect diversity and 8 kHz telephony acoustics) rather than clean English-centric benchmarks.
- **Acoustic Guardrails:** Never rely on single-letter phonetic spelling over 8 kHz PSTN without confirmation; speak case codes slowly with chunking (`JS-48-29`, repeated twice).

## 2. Sub-800ms Conversational Turn-Taking Latency Budget
In human phone conversations, silences longer than `~1,000 ms` make callers think the line dropped and cause double-talk collisions. Budget every millisecond across a streaming pipeline:

| Stage | Target Latency | Engineering Technique |
|---|---|---|
| **Endpointing (VAD + Semantic EoU)** | `150–200 ms` | **Silero VAD** + semantic end-of-utterance classifier (distinguishes mid-thought hesitation *"um..."* from completed answers). |
| **Streaming ASR Finalization** | `180–250 ms` | Incremental WebRTC/SIP frame streaming (never wait for full-file upload). |
| **LLM / Slot Extractor TTFT** | `200–250 ms` | Compact structured-output model with cached system prompt + local colloquial synonym map (`rythu`→farmer, `white card`→BPL ration, `velu`→thousand). |
| **Streaming TTS TTFB** | `120–150 ms` | Sentence-clause streaming TTS with instant **barge-in cancellation** (stop playback immediately if Silero VAD detects caller speech `> 200 ms`). |
| **Total Turn-Around** | **`~700–800 ms`** | Feels natural on basic phone calls. |

## 3. Cognitive Load & Non-Trapping Voice Design
- **Cowan's Working-Memory Ceiling (2001):** Humans hold only **3–4 chunks** in audio-only working memory (no visual scrollback!). Never read 10 schemes or 6 menu choices aloud—present the **top 3 highest-value schemes**, offer *"say 'more' for the rest,"* and send the complete checklist to the visiting agent.
- **Multi-Slot Extraction:** Extract volunteered facts simultaneously (*"Nenu farm worker, 65 years, white card undi"* → 3 slots filled in 1 turn).
- **3-Step Non-Trapping Recovery Ladder:** Noise (`confidence < 0.70`) → short spoken Yes/No mode; `Miss 1` → simpler rephrase; `Miss 2` → 2 spoken choices; `Miss 3 / silence` → flag `verify_at_visit` for the village CSC operator/postman.
- **Zero-PII Active Interruption:** Never ask for Aadhaar, OTP, or bank digits; if spoken anyway, interrupt politely and overwrite digits with `[REDACTED]` before state persistence.

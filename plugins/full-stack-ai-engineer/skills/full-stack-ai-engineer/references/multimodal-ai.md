# Multimodal, Voice, and Document Intelligence

Check the chosen provider's current docs for supported input types, size limits, and pricing before designing. Do not assume a model accepts a modality.

## Images and vision
- Decide the task first: description, classification, extraction (receipts, forms), UI/screenshot understanding, or comparison. Extraction tasks need structured output and validation.
- Resize and compress images to the provider's recommended dimensions; large images raise cost and latency without improving results.
- Send only the pages or regions needed. Crop when the target is small.
- Validate extracted fields (types, ranges, checksums). Keep the source image reference for audit.
- Moderate user uploads; strip EXIF location data unless needed.

## Audio and speech
- **Speech to text:** choose between hosted APIs and local models by latency, accuracy, language, and privacy. Handle diarization and timestamps if needed. Chunk long audio with overlap and merge.
- **Text to speech:** stream audio as it is generated; pick voices consistent with your product; disclose synthetic voice where required.
- Normalize audio (sample rate, mono) and cap upload size and duration.

## Voice AI and real-time interaction
- Architecture: client mic -> streaming transport (WebRTC or WebSocket) -> speech recognition -> LLM -> speech synthesis -> client playback. Some providers offer speech-to-speech realtime APIs that collapse these stages; evaluate both.
- Latency budget matters most: measure time to first audio. Stream every stage, keep prompts short, and start synthesis on the first complete sentence.
- **Turn-taking:** voice activity detection, end-of-utterance timeouts, and **barge-in** (stop playback when the user speaks).
- Keep responses short and speakable; avoid markdown, URLs, and long lists in spoken output.
- Handle noisy audio, silence, dropped connections, and reconnects. Provide a text fallback.
- Confirm consequential actions verbally and by a second channel when possible.
- Respect consent and recording laws; show a clear recording indicator; define retention.

## Video
- Sample frames at a rate that fits the task (scene change or fixed interval) rather than sending every frame; pair with transcript and timestamps.
- Process asynchronously via queue; return results with time ranges.
- Watch cost: video multiplies tokens quickly.

## Document intelligence and OCR
1. **Classify** the document type (invoice, contract, report, scan, form).
2. **Parse**: use native text extraction first; use OCR or a layout-aware parser for scans, tables, and multi-column pages.
3. **Structure**: preserve headings, tables, page numbers, and bounding boxes as metadata.
4. **Extract** fields with a JSON schema; validate (dates, currency, totals reconcile).
5. **Route low confidence** results to human review with the source region highlighted.
6. **Index** for RAG with page and section metadata so citations can point to the exact page.

Evaluate extraction with a labeled sample: per-field accuracy, not just overall.

## Workflow orchestration
Use a workflow engine or durable queue when a pipeline has multiple steps, retries, waits, or human approvals (for example ingest -> OCR -> extract -> review -> publish).
- Make each step idempotent and checkpointed; store state outside the process.
- Define retry policy and dead-letter handling per step.
- Prefer a deterministic workflow with LLM calls inside steps over a free-form agent when the process is known.
- Provide visibility: run status, step logs, and a way to replay or resume.

## Streaming structured outputs
- Stream text for chat; for JSON, either stream partial JSON into a tolerant parser for progressive UI, or wait for the complete object before acting.
- Never execute or persist partial structured output. Validate the final object against the schema.
- On validation failure, retry once with the error message; then fall back or surface an error.
- Provide the UI a stable event shape (token, partial_object, tool_status, final, error).

## Safety for multimodal inputs
- Images, audio, and documents can contain hidden or visible instructions; treat extracted content as untrusted data.
- Scan uploads for type, size, and malware where applicable.
- Handle faces, IDs, medical, and financial documents as sensitive: minimize storage, redact in logs, and check provider data terms.

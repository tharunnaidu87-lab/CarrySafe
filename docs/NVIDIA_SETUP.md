# NVIDIA configuration

Selected provider: NVIDIA hosted NIM API. Verified against NVIDIA documentation on 23 October 2026; live credential/model interaction remains unverified.

| Setting | Value |
|---|---|
| `LLM_BASE_URL` | `https://integrate.api.nvidia.com/v1` |
| `LLM_MODEL` | `nvidia/nemotron-3.5-lightning-30b-a3b` |
| `LLM_API_KEY` | Your NVIDIA API key, entered in Render Environment settings |

The selected model page currently offers a trial API endpoint and describes agentic use. Its API documentation covers tool-use training. This does not establish that CarrySafe's full schema and orchestration have passed live testing. Availability and trial limits may change.

1. Open [the NVIDIA model page](https://build.nvidia.com/nvidia/nemotron-3.5-lightning-30b-a3b), sign in and use its Generate API Key flow.
2. Open [CarrySafe Environment](https://dashboard.render.com/web/srv-dbdi1jtg1s2s73bj1rlg/env), add the three values above and choose **Save and deploy**. Never commit the key or send it in screenshots.
3. Verify a read that requires both unresolved-incident and overdue-control tools. Inspect actual tool traces.
4. Request a synthetic report, review the proposed fields, confirm it, then query the persisted incident. Confirm that missing fields and unauthorized closure are handled correctly.
5. Check latency, response truncation and schema compatibility against the real provider. Adjust model parameters only after observing actual behavior; mock tests do not substitute for this gate.

The base URL excludes `/chat/completions`, which CarrySafe appends itself. No NVIDIA SDK is required because the existing adapter uses HTTP and the OpenAI-compatible request format. Do not paste an API key into the browser application's chat.

Sources:
- https://build.nvidia.com/nvidia/nemotron-3.5-lightning-30b-a3b
- https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-5-lightning-30b-a3b

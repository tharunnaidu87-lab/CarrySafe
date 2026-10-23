# Reproducible demonstration

The supplied fixture contains 100 synthetic cases. CS-1042 is a pipe leak at Loading Bay 2, with Alex as accepted owner and an overdue temporary containment review. Two handovers connect morning, evening and night. The overdue state comes from fixture timestamps, not a modified production clock.

## Before recording

1. Complete setup, start the application and open http://localhost:8000.
2. Keep three separate browser profiles/private sessions ready if demonstrating Alex, Sam and Jordan in parallel. All use the local password you chose.
3. If using natural language, configure the exact LLM endpoint/key/model and verify a real request before recording. Otherwise describe the demonstration as manual MCP mode. Do not pretend the fixed shortcut is LLM reasoning.
4. Run `scripts/verify_mcp.py` and retain its actual output for the technical evidence segment.
5. Rehearse the browser flow below; browser automation was prepared but not run in the build environment.

## Click sequence

**Alex / reporting:** Sign in as `alex@demo.carrysafe.test`. Click Report incident. Enter a clearly synthetic report; select Loading Bay 2, Shift A — Morning and Alex as owner. Review change, then Confirm and save. The response includes a case card and actual MCP write activity. Open the card and add a temporary measure with an explicit future review date. The microphone, when supported, creates editable text; it never submits automatically.

**Incoming shift:** Open Shift handovers. Inspect the three shifts and carried case cards. Sign in as Sam in a separate session. Acknowledge the morning-to-evening handover with confirmation. Open CS-1042 to show that acknowledgment left its active control and incident state intact.

**Multi-step MCP:** On Assistant, click Brief me on the handover. The backend calls list_open_incidents, list_overdue_controls and get_shift_handover over HTTP. Expand each Tool activity item to show the negotiated protocol and returned records. Free-form AI can perform the same orchestration only with a configured working model.

**Integrity:** Open Integrity center. Show an overdue control review, missing owner acceptance and an unacknowledged handover. Explain that these indicate missing process evidence, not a prediction of physical danger.

**Closure gate:** As Alex, open CS-1042 and Request closure review. Use an explicit synthetic maintenance work-order reference. A worker has no approval button. Show the verification script's actual worker-denial result if needed. As Jordan, open the case's pending closure request, choose approval and supply the required reason and verification reference. Attempt approval while the control is still active: the backend rejects it with ACTIVE_CONTROL.

**Authorized completion:** Still as Jordan, Record review on the control; select retired and supply a synthetic inspection observation. Reopen Review request using the refreshed case version, provide the independent verification reference and approve. The case becomes closed. The accountability trail preserves the initial report, denied attempt, control review and final decision. The handover snapshot still contains the case but resolves its current closed state.

## Under-three-minute narration

- **0:00–0:15:** “When a shift ends, temporary measures can outlive the person who introduced them. CarrySafe keeps the issue, its owner and the follow-up connected.”
- **0:15–0:45:** Report a synthetic incident, review the proposed details and confirm. “This creates a database record through the actual MCP server.” If a live LLM is verified, show natural-language reporting here.
- **0:45–1:15:** Run the handover briefing and expand activity. “These are three real MCP calls: unfinished work, overdue controls and handover records.”
- **1:15–1:40:** Open Integrity center and CS-1042. “The review is overdue. CarrySafe explains the missing check without pretending it can inspect the workplace.”
- **1:40–2:10:** Show worker denial evidence and premature supervisor approval rejection. “Neither the model nor a role label can bypass required evidence and control retirement.”
- **2:10–2:40:** Record the supervisor control review and approve the closure request. Show the history. “The final state follows an attributable review, while the original report and rejected attempt remain visible.”
- **2:40–2:55:** Show SDK/protocol test output. “CarrySafe is an Alexa+-ready MCP capability demonstrated in our web client. Its focus is continuity and accountable action.”

## Safe local reset

Stop the server. From the repository root run:

```powershell
.venv\Scripts\python.exe scripts\reset_demo.py
```

Linux/macOS use `.venv/bin/python`. The reset refuses PostgreSQL and non-synthetic or multi-organization databases. It requires the exact confirmation phrase, archives the previous SQLite database, asks for a new local password, reruns migrations and seeds a fresh synthetic fixture. It does not delete production data. Restart the server afterward.

The video must be recorded and published by the team. No YouTube/Vimeo upload or Devpost submission has been performed.

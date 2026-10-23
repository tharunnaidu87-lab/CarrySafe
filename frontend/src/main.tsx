import React, { useState, useEffect, useRef } from "react";
import { createRoot } from "react-dom/client";
import {
  BrowserRouter,
  NavLink,
  Routes,
  Route,
  useParams,
} from "react-router-dom";
import {
  QueryClient,
  QueryClientProvider,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import {
  ShieldCheck,
  MessageSquare,
  LayoutDashboard,
  ArrowRightLeft,
  ScanLine,
  ClipboardCheck,
  ArrowUpRight,
  ArrowUp,
  Mic,
  MicOff,
  Plus,
  LogOut,
  Check,
  ChevronRight,
  Activity,
  Clock,
  AlertTriangle,
  Search,
  X,
  Radio,
  Volume2,
} from "lucide-react";
import { api, human, date, convert, type Json } from "./api";
import "./style.css";
const qc = new QueryClient({
  defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } },
});
const Context = React.createContext<Json>({});
const useUser = () => React.useContext(Context);
function useData(name: string, extra = "") {
  return useQuery({
    queryKey: [name, extra],
    queryFn: () => api("/data/" + name + extra),
  });
}
function Badge({
  children,
  tone = "neutral",
}: {
  children: React.ReactNode;
  tone?: string;
}) {
  return <span className={"badge " + tone}>{children}</span>;
}
function ErrorBox({ error }: { error: unknown }) {
  return error ? (
    <div className="error" role="alert">
      <AlertTriangle size={16} />
      {String(error instanceof Error ? error.message : error)}
    </div>
  ) : null;
}
function Empty({ children }: { children: React.ReactNode }) {
  return <div className="empty">{children}</div>;
}
function Heading({
  eyebrow,
  title,
  subtitle,
  action,
}: {
  eyebrow: string;
  title: string;
  subtitle: string;
  action?: React.ReactNode;
}) {
  return (
    <header className="page-heading">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      {action}
    </header>
  );
}
function Login() {
  const [email, setEmail] = useState("alex@demo.carrysafe.test"),
    [password, setPassword] = useState(""),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  const query = useQueryClient();
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api("/login", { email, password });
      await query.invalidateQueries({ queryKey: ["me"] });
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="login-page">
      <section className="login-story">
        <div className="brand">
          <ShieldCheck />
          <span>
            CarrySafe<span className="brand-dot">.</span>
          </span>
        </div>
        <div>
          <div className="eyebrow">CONTINUITY IS A RESPONSIBILITY</div>
          <h1>
            The shift ends.
            <br />
            The responsibility
            <br />
            <em>carries forward.</em>
          </h1>
          <p>
            Keep temporary safeguards, unfinished work and the next person
            connected.
          </p>
        </div>
        <div className="login-foot">
          VOICE-FIRST HANDOVERS <span>01 / 03</span>
        </div>
      </section>
      <section className="login-form">
        <Badge tone="amber">WORKSPACE ACCESS</Badge>
        <h2>Start with what matters.</h2>
        <p>Sign in to your CarrySafe workspace.</p>
        <form onSubmit={submit}>
          <label>
            Email address
            <input
              autoComplete="username"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>
          <ErrorBox error={error} />
          <button className="primary wide" disabled={busy}>
            {busy ? "Signing in…" : "Enter workspace"}
            <ArrowUpRight size={18} />
          </button>
        </form>
        <div className="login-note">
          <ShieldCheck size={18} />
          <p>
            Demo accounts contain synthetic records only. Use the password you
            set during local setup.
          </p>
        </div>
      </section>
    </div>
  );
}
function App() {
  const me = useQuery({ queryKey: ["me"], queryFn: () => api("/me") });
  if (me.isPending) return <Empty>Connecting to your workspace…</Empty>;
  return me.data ? (
    <Context.Provider value={me.data}>
      <Shell />
    </Context.Provider>
  ) : (
    <Login />
  );
}
const nav = [
  ["/", "Assistant", MessageSquare],
  ["/operations", "Operations", LayoutDashboard],
  ["/handover", "Shift handovers", ArrowRightLeft],
  ["/integrity", "Integrity center", ScanLine],
  ["/review", "Supervisor review", ClipboardCheck],
] as const;
function Shell() {
  const { user, ai_enabled } = useUser();
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <NavLink to="/" className="brand">
          <ShieldCheck />
          <span>
            CarrySafe<span className="brand-dot">.</span>
          </span>
        </NavLink>
        <div className="workspace">
          <span className="workspace-icon">N</span>
          <div>
            <strong>Northpoint Logistics</strong>
            <small>Demo facility · Synthetic data</small>
          </div>
        </div>
        <div className="nav-caption">WORKSPACE</div>
        <nav>
          {nav.map(([to, label, Icon]) => (
            <NavLink key={to} to={to} end>
              <Icon size={18} />
              {label}
              {to === "/" && <span className="nav-dot" />}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="system-status">
            <span className="status-dot" />
            Persistent records
            <small>
              {ai_enabled
                ? "AI provider configured"
                : "Manual MCP mode · AI not configured"}
            </small>
          </div>
          <div className="account">
            <div className="avatar">
              {user.name
                .split(" ")
                .map((x: string) => x[0])
                .join("")}
            </div>
            <div>
              <strong>{user.name}</strong>
              <small>{human(user.role)}</small>
            </div>
            <button
              className="icon-button"
              aria-label="Sign out"
              onClick={async () => {
                await api("/logout", {});
                qc.clear();
                location.reload();
              }}
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <div className="topbar">
          <span>
            <span className="status-dot" /> NORTHPOINT / OPERATIONS
          </span>
          <span className="topbar-right">
            <Badge>SYNTHETIC DEMO</Badge>
            <span>IST · UTC+05:30</span>
            <button
              className="icon-button mobile-logout"
              aria-label="Sign out on mobile"
              onClick={async () => {
                await api("/logout", {});
                location.reload();
              }}
            >
              <LogOut size={15} />
            </button>
          </span>
        </div>
        <main>
          <Routes>
            <Route path="/" element={<Assistant />} />
            <Route path="/operations" element={<Operations />} />
            <Route path="/incidents/:id" element={<IncidentPage />} />
            <Route path="/handover" element={<Handovers />} />
            <Route path="/integrity" element={<Integrity />} />
            <Route path="/review" element={<Review />} />
          </Routes>
        </main>
        <footer>
          CarrySafe coordinates records. Physical safety decisions remain with
          qualified personnel.
        </footer>
      </div>
    </div>
  );
}
function OperationDialog({
  name,
  defaults = {},
  close,
  onResult,
}: {
  name: string;
  defaults?: Json;
  close: () => void;
  onResult?: (r: Json) => void;
}) {
  const tools = useQuery({ queryKey: ["tools"], queryFn: () => api("/tools") });
  const dir = useData("get_directory");
  const { user } = useUser();
  const [values, setValues] = useState<Json>(
      Object.fromEntries(
        Object.entries(defaults).map(([k, v]) => [k, String(v ?? "")]),
      ),
    ),
    [stage, setStage] = useState(false),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  const id = useRef(crypto.randomUUID());
  const spec = tools.data?.[name],
    props = spec?.schema.properties || {};
  const payload = () =>
    Object.fromEntries(
      Object.entries(props)
        .map(([k, s]) => [k, convert(String(values[k] ?? ""), s as Json)])
        .filter(([, v]) => v !== undefined),
    );
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!stage) {
      setStage(true);
      return;
    }
    setBusy(true);
    setError("");
    try {
      const result = await api("/operations/" + name, {
        payload: payload(),
        request_id: id.current,
        confirmed: true,
      });
      await qc.invalidateQueries();
      onResult?.(result);
      close();
    } catch (e) {
      setError(String(e));
      setStage(false);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="modal-backdrop">
      <section
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label={human(name)}
      >
        <div className="modal-heading">
          <h2>{human(name)}</h2>
          <button
            className="icon-button"
            aria-label="Close dialog"
            onClick={close}
          >
            <X />
          </button>
        </div>
        <p>{spec?.description}</p>
        <ErrorBox error={error || tools.error || dir.error} />
        {!spec ? (
          <Empty>Loading form…</Empty>
        ) : (
          <form onSubmit={submit}>
            {stage ? (
              <div className="confirmation">
                <Badge tone="amber">CONFIRM CHANGE</Badge>
                <p>
                  Review these details. This action will be recorded under{" "}
                  {user.name}.
                </p>
                <dl>
                  {Object.entries(payload()).map(([k, v]) => (
                    <React.Fragment key={k}>
                      <dt>{human(k)}</dt>
                      <dd>{String(v)}</dd>
                    </React.Fragment>
                  ))}
                </dl>
              </div>
            ) : (
              <div className="form-grid">
                {Object.entries(props).map(([key, raw]) => {
                  const s = raw as Json;
                  if (
                    key === "expected_version" ||
                    (key === "incident_id" && defaults.incident_id)
                  )
                    return null;
                  const type =
                    s.type ||
                    s.anyOf?.find((x: Json) => x.type !== "null")?.type;
                  const isDate =
                    s.format === "date-time" ||
                    s.anyOf?.some((x: Json) => x.format === "date-time");
                  const choices =
                    key === "location_id"
                      ? dir.data?.locations
                      : ["shift_id", "outgoing_id", "incoming_id"].includes(key)
                        ? dir.data?.shifts
                        : [
                              "owner_id",
                              "responsible_id",
                              "recipient_id",
                            ].includes(key)
                          ? dir.data?.users
                          : null;
                  const required = spec.schema.required?.includes(key);
                  const change = (v: string) =>
                    setValues({ ...values, [key]: v });
                  return (
                    <label key={key}>
                      {human(key)}
                      {required ? " *" : ""}
                      {choices ? (
                        <select
                          required={required}
                          value={values[key] ?? ""}
                          onChange={(e) => change(e.target.value)}
                        >
                          <option value="">Choose…</option>
                          {choices.map((x: Json) => (
                            <option key={x.id} value={x.id}>
                              {x.name}
                            </option>
                          ))}
                        </select>
                      ) : s.enum || type === "boolean" ? (
                        <select
                          required={required}
                          value={values[key] ?? ""}
                          onChange={(e) => change(e.target.value)}
                        >
                          <option value="">Choose…</option>
                          {(s.enum || ["true", "false"]).map((x: string) => (
                            <option key={x} value={x}>
                              {human(x)}
                            </option>
                          ))}
                        </select>
                      ) : [
                          "description",
                          "note",
                          "evidence",
                          "observation",
                          "reason",
                          "verification_reference",
                        ].includes(key) ? (
                        <textarea
                          required={required}
                          minLength={s.minLength}
                          maxLength={s.maxLength}
                          value={values[key] ?? ""}
                          onChange={(e) => change(e.target.value)}
                        />
                      ) : (
                        <input
                          required={required}
                          type={
                            isDate
                              ? "datetime-local"
                              : type === "integer"
                                ? "number"
                                : "text"
                          }
                          value={values[key] ?? ""}
                          onChange={(e) => change(e.target.value)}
                        />
                      )}
                    </label>
                  );
                })}
              </div>
            )}
            <div className="modal-actions">
              <button
                type="button"
                className="secondary"
                onClick={() => (stage ? setStage(false) : close())}
              >
                {stage ? "Edit details" : "Cancel"}
              </button>
              <button className="primary" disabled={busy}>
                {busy
                  ? "Saving…"
                  : stage
                    ? "Confirm and save"
                    : "Review change"}
                <ChevronRight size={16} />
              </button>
            </div>
          </form>
        )}
      </section>
    </div>
  );
}
function CaseCard({ incident: i }: { incident: Json }) {
  return (
    <NavLink className="case-card" to={"/incidents/" + i.id}>
      <div>
        <span className="mono">{i.id}</span>
        <Badge tone={i.state === "closed" ? "green" : "amber"}>
          {human(i.state)}
        </Badge>
      </div>
      <h3>{i.description.replace(/^SYNTHETIC: /, "")}</h3>
      <p>
        {i.location} · {i.owner || "Unassigned"}
      </p>
      <div className="case-foot">
        <span>
          {i.controls?.filter((x: Json) => x.state === "active").length || 0}{" "}
          active measures
        </span>
        <ArrowUpRight size={16} />
      </div>
    </NavLink>
  );
}
function Facts({ trace }: { trace: Json[] }) {
  const cases = new Map<string, Json>();
  trace.forEach((t) => {
    t.data?.incidents?.forEach((i: Json) => cases.set(i.id, i));
    if (t.data?.id && t.data?.description) cases.set(t.data.id, t.data);
  });
  return (
    <>
      <div className="case-grid">
        {[...cases.values()].slice(0, 4).map((i) => (
          <CaseCard key={i.id} incident={i} />
        ))}
      </div>
      {trace.map((t, n) =>
        t.data?.controls ? (
          <div className="fact-line" key={n}>
            <Clock size={16} />
            {t.data.controls.length} overdue reviews returned by MCP
          </div>
        ) : t.data?.flags ? (
          <div className="fact-line" key={n}>
            <AlertTriangle size={16} />
            {t.data.flags.length} integrity flags returned by MCP
          </div>
        ) : t.data?.handovers ? (
          <div className="fact-line" key={n}>
            <ArrowRightLeft size={16} />
            {t.data.handovers.length} handovers retrieved
          </div>
        ) : null,
      )}
    </>
  );
}
function Assistant() {
  const { ai_enabled, user } = useUser();
  const dashboard = useData("get_dashboard");
  const [input, setInput] = useState(""),
    [messages, setMessages] = useState<Json[]>([]),
    [trace, setTrace] = useState<Json[]>([]),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [pending, setPending] = useState<Json | null>(null),
    [report, setReport] = useState(false),
    [listening, setListening] = useState(false),
    [speak, setSpeak] = useState(false);
  const conversation = useRef<string | null>(
      localStorage.getItem("cs-conversation-" + user.id),
    ),
    recognition = useRef<any>(null),
    end = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (conversation.current)
      api("/conversations/" + conversation.current)
        .then((c) => {
          setMessages(c.messages);
          setPending(c.pending);
        })
        .catch(() => {
          conversation.current = null;
        });
    return () => recognition.current?.abort();
  }, []);
  useEffect(() => {
    end.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [messages]);
  function receive(r: Json) {
    setMessages((m) => [
      ...m,
      { role: "assistant", content: r.answer, trace: r.trace },
    ]);
    setTrace(r.trace || []);
    setPending(r.pending || null);
    if (r.conversation_id) {
      conversation.current = r.conversation_id;
      localStorage.setItem("cs-conversation-" + user.id, r.conversation_id);
    }
    if (speak && "speechSynthesis" in window) {
      speechSynthesis.cancel();
      speechSynthesis.speak(
        new SpeechSynthesisUtterance(r.answer.slice(0, 500)),
      );
    }
  }
  async function run(message: string, shortcut?: string) {
    setBusy(true);
    setError("");
    setMessages((m) => [...m, { role: "user", content: message }]);
    try {
      receive(
        await api(
          shortcut ? "/assistant/shortcut" : "/assistant/chat",
          shortcut
            ? { command: shortcut }
            : { conversation_id: conversation.current, message },
        ),
      );
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }
  async function confirm(approve: boolean) {
    if (!pending) return;
    setBusy(true);
    try {
      receive(
        await api("/assistant/confirm", {
          conversation_id: conversation.current,
          proposal_id: pending.id,
          approve,
        }),
      );
      qc.invalidateQueries();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }
  function microphone() {
    if (listening) {
      recognition.current?.stop();
      return;
    }
    const Speech =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;
    if (!Speech) {
      setError(
        "Speech recognition is unavailable in this browser. Type your message below.",
      );
      return;
    }
    const r = new Speech();
    r.lang = "en-IN";
    r.interimResults = true;
    r.onstart = () => setListening(true);
    r.onend = () => setListening(false);
    r.onerror = (e: any) => {
      setError("Microphone: " + e.error + ". You can continue by typing.");
      setListening(false);
    };
    r.onresult = (e: any) =>
      setInput(
        Array.from(e.results)
          .map((x: any) => x[0].transcript)
          .join(" "),
      );
    recognition.current = r;
    r.start();
  }
  return (
    <>
      <Heading
        eyebrow="YOUR SHIFT, CONNECTED"
        title="Nothing left behind."
        subtitle="Ask about unfinished work. Carry the right context into the next shift."
        action={
          <button className="primary" onClick={() => setReport(true)}>
            <Plus size={17} />
            Report incident
          </button>
        }
      />
      <div className="assistant-layout">
        <section className="conversation">
          <div className="section-bar">
            <span>
              <MessageSquare size={17} />
              CarrySafe assistant
            </span>
            <Badge tone={ai_enabled ? "green" : "neutral"}>
              {ai_enabled ? "AI + MCP" : "LIVE MCP · MANUAL MODE"}
            </Badge>
          </div>
          <div className="conversation-content" aria-live="polite">
            {messages.length === 0 ? (
              <div className="welcome">
                <div className="assistant-mark">
                  <ShieldCheck size={28} />
                </div>
                <div className="eyebrow">READY FOR THE NEXT SHIFT</div>
                <h2>What needs your attention?</h2>
                <p>
                  Your records, responsibilities and temporary measures —<br />
                  connected across every handover.
                </p>
                <div className="suggestions">
                  <button
                    onClick={() =>
                      run(
                        "What is unfinished, and which reviews are overdue?",
                        "briefing",
                      )
                    }
                  >
                    <ArrowRightLeft />
                    <div>
                      <strong>Brief me on the handover</strong>
                      <small>Open incidents + overdue reviews + shifts</small>
                    </div>
                    <ArrowUpRight />
                  </button>
                  <button
                    onClick={() =>
                      run("Show the integrity flags.", "integrity")
                    }
                  >
                    <ScanLine />
                    <div>
                      <strong>Check what needs attention</strong>
                      <small>
                        Explain missing reviews and responsibilities
                      </small>
                    </div>
                    <ArrowUpRight />
                  </button>
                </div>
                <div className="mode-note">
                  {ai_enabled
                    ? "Natural-language requests use your configured model."
                    : "No model key configured. These shortcuts use real MCP tools; free-form AI becomes available after setup."}
                </div>
              </div>
            ) : (
              messages.map((m, n) => (
                <div className={"message " + m.role} key={n}>
                  <div className="message-author">
                    {m.role === "user" ? user.name : "CarrySafe"}
                    <span>
                      {m.trace?.length ? "DATABASE-BACKED RESPONSE" : ""}
                    </span>
                  </div>
                  <div className="message-text">{m.content}</div>
                  {m.trace && <Facts trace={m.trace} />}
                </div>
              ))
            )}
            {pending && (
              <div className="proposal">
                <Badge tone="amber">AWAITING YOUR CONFIRMATION</Badge>
                <h3>{human(pending.tool)}</h3>
                <pre>{JSON.stringify(pending.payload, null, 2)}</pre>
                <button
                  className="primary"
                  disabled={busy}
                  onClick={() => confirm(true)}
                >
                  Confirm change
                </button>
                <button
                  className="secondary"
                  disabled={busy}
                  onClick={() => confirm(false)}
                >
                  Cancel
                </button>
              </div>
            )}
            {busy && (
              <div className="working">
                <Activity size={16} />
                Retrieving and validating…
              </div>
            )}
            <ErrorBox error={error} />
            <div ref={end} />
          </div>
          <form
            className="composer"
            onSubmit={(e) => {
              e.preventDefault();
              if (input.trim()) {
                run(input);
                setInput("");
              }
            }}
          >
            <textarea
              aria-label="Message CarrySafe"
              placeholder={
                listening
                  ? "Listening… review the transcript before sending."
                  : "Ask CarrySafe about this shift…"
              }
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <div className="composer-bottom">
              <span>
                {listening
                  ? "LISTENING · EDIT BEFORE SENDING"
                  : "Actions require your confirmation"}
              </span>
              <div>
                <button
                  type="button"
                  className={"icon-button " + (speak ? "selected" : "")}
                  aria-label="Toggle spoken responses"
                  onClick={() => setSpeak(!speak)}
                >
                  <Volume2 size={17} />
                </button>
                <button
                  type="button"
                  className={"icon-button " + (listening ? "listening" : "")}
                  aria-label={
                    listening ? "Stop microphone" : "Start microphone"
                  }
                  onClick={microphone}
                >
                  {listening ? <MicOff size={18} /> : <Mic size={18} />}
                </button>
                <button
                  className="send"
                  aria-label="Send message"
                  disabled={busy || !!pending || !input.trim()}
                >
                  <ArrowUp size={18} />
                </button>
              </div>
            </div>
          </form>
        </section>
        <aside className="context-panel">
          <section className="shift-card">
            <div className="eyebrow">WORKSPACE PULSE</div>
            <h3>
              Carry forward.
              <br />
              Follow through.
            </h3>
            <div className="pulse-row">
              <span>Unresolved incidents</span>
              <strong>{dashboard.data?.active ?? "—"}</strong>
            </div>
            <div className="pulse-row">
              <span>Overdue reviews</span>
              <strong className="amber-text">
                {dashboard.data?.overdue ?? "—"}
              </strong>
            </div>
            <div className="pulse-row">
              <span>Pending handovers</span>
              <strong>{dashboard.data?.unacknowledged ?? "—"}</strong>
            </div>
            <NavLink to="/handover" className="text-link">
              Open handover center
              <ArrowUpRight size={16} />
            </NavLink>
          </section>
          <section className="tool-panel">
            <div className="section-bar">
              <span>
                <Radio size={15} />
                Tool activity
              </span>
              <span className="mono">MCP</span>
            </div>
            {trace.length ? (
              trace.map((t, n) => (
                <details key={n}>
                  <summary>
                    <span className={t.is_error ? "red-text" : "green-text"}>
                      {t.is_error ? "!" : "✓"}
                    </span>
                    <span>
                      {t.tool}
                      <small>{t.protocol} · Streamable HTTP</small>
                    </span>
                  </summary>
                  <pre>{JSON.stringify(t.data || t.text, null, 2)}</pre>
                </details>
              ))
            ) : (
              <div className="tool-empty">
                <Activity size={24} />
                <p>
                  Actual tool calls appear here
                  <br />
                  when you ask a question.
                </p>
              </div>
            )}
          </section>
          <div className="integrity-note">
            <ShieldCheck size={18} />
            <p>
              <strong>Confirmation is built in.</strong>The assistant cannot
              override roles, verification or closure rules.
            </p>
          </div>
        </aside>
      </div>
      {report && (
        <OperationDialog
          name="create_incident"
          close={() => setReport(false)}
        />
      )}
    </>
  );
}
function IncidentTable({ incidents }: { incidents: Json[] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Case / Report</th>
            <th>Location</th>
            <th>Responsibility</th>
            <th>State</th>
            <th>Updated</th>
          </tr>
        </thead>
        <tbody>
          {incidents.map((i) => (
            <tr key={i.id}>
              <td>
                <NavLink className="table-link" to={"/incidents/" + i.id}>
                  <span className="mono">{i.id}</span>
                  <strong>{i.description.replace(/^SYNTHETIC: /, "")}</strong>
                </NavLink>
              </td>
              <td>{i.location}</td>
              <td>
                {i.owner || "Unassigned"}
                <small>
                  {i.owner_accepted ? "Accepted" : "Acceptance pending"}
                </small>
              </td>
              <td>
                <Badge tone={i.state === "closed" ? "green" : "amber"}>
                  {human(i.state)}
                </Badge>
              </td>
              <td className="muted">{date(i.updated_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
function Operations() {
  const stats = useData("get_dashboard"),
    [search, setSearch] = useState(""),
    [report, setReport] = useState(false),
    items = useData(
      "list_open_incidents",
      "?query=" + encodeURIComponent(search),
    );
  return (
    <>
      <Heading
        eyebrow="OPERATIONS OVERVIEW"
        title="The work in progress."
        subtitle="Live records from your workspace. Every number has a case behind it."
        action={
          <button className="primary" onClick={() => setReport(true)}>
            <Plus size={16} />
            Report incident
          </button>
        }
      />
      <div className="stats-grid">
        {[
          ["active", "Open incidents"],
          ["active_controls", "Active measures"],
          ["overdue", "Overdue reviews"],
          ["unassigned", "Unaccepted ownership"],
        ].map(([key, title]) => (
          <div className="stat" key={key}>
            <span>{title}</span>
            <strong className={key === "overdue" ? "amber-text" : ""}>
              {stats.data?.[key] ?? "—"}
            </strong>
            <small>
              {key === "overdue"
                ? "Review required; not proof of failure"
                : "From persisted workspace records"}
            </small>
          </div>
        ))}
      </div>
      <section className="panel">
        <div className="section-bar">
          <h2>Unresolved incidents</h2>
          <label className="search">
            <Search size={16} />
            <input
              aria-label="Search incidents"
              placeholder="Search reports or case IDs"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </label>
        </div>
        <ErrorBox error={items.error || stats.error} />
        {items.isPending ? (
          <Empty>Loading incidents…</Empty>
        ) : items.data?.incidents.length ? (
          <IncidentTable incidents={items.data.incidents} />
        ) : (
          <Empty>No incidents match your search.</Empty>
        )}
        <div className="table-note">
          Showing up to 50 matching cases. Narrow your search for a specific
          case.
        </div>
      </section>
      {report && (
        <OperationDialog
          name="create_incident"
          close={() => setReport(false)}
        />
      )}
    </>
  );
}
function IncidentPage() {
  const { id } = useParams(),
    info = useData("get_incident", "?incident_id=" + id),
    history = useData("get_incident_history", "?incident_id=" + id),
    { user } = useUser();
  const [action, setAction] = useState<Json | null>(null),
    i = info.data;
  if (!i)
    return (
      <>
        <ErrorBox error={info.error} />
        <Empty>Loading case…</Empty>
      </>
    );
  const open = (name: string, extra: Json = {}) =>
    setAction({
      name,
      defaults: { incident_id: i.id, expected_version: i.version, ...extra },
    });
  return (
    <>
      <Heading
        eyebrow={"INCIDENT WORKSPACE / " + i.id}
        title={i.description.replace(/^SYNTHETIC: /, "")}
        subtitle={
          i.location +
          " · Version " +
          i.version +
          " · Updated " +
          date(i.updated_at)
        }
        action={
          <Badge tone={i.state === "closed" ? "green" : "amber"}>
            {human(i.state)}
          </Badge>
        }
      />
      <div className="detail-layout">
        <div>
          <section className="panel padded">
            <h2>Responsibility & record</h2>
            <dl>
              <dt>Original report</dt>
              <dd>{i.description}</dd>
              <dt>Owner</dt>
              <dd>
                {i.owner || "Unassigned"} ·{" "}
                {i.owner_accepted ? "Accepted" : "Not accepted"}
              </dd>
              <dt>Information status</dt>
              <dd>
                {i.disputed
                  ? "Conflicting reports — clarification required"
                  : "No structured dispute recorded"}
              </dd>
            </dl>
            {i.state !== "closed" && (
              <div className="action-row">
                {i.owner_id === user.id && !i.owner_accepted && (
                  <button
                    className="secondary"
                    onClick={() => open("accept_ownership")}
                  >
                    Accept ownership
                  </button>
                )}
                {user.role === "supervisor" && (
                  <button
                    className="secondary"
                    onClick={() => open("assign_incident")}
                  >
                    Assign owner
                  </button>
                )}
                <button
                  className="secondary"
                  onClick={() => open("record_incident_progress")}
                >
                  Record update
                </button>
                <button
                  className="secondary"
                  onClick={() => open("add_temporary_control")}
                >
                  Add temporary measure
                </button>
                {i.state === "open" && (
                  <button
                    className="primary"
                    onClick={() => open("request_incident_closure")}
                  >
                    Request closure review
                  </button>
                )}
              </div>
            )}
          </section>
          <section className="panel padded">
            <div className="section-title">
              <h2>Temporary measures</h2>
              <span className="mono">{i.controls.length}</span>
            </div>
            {i.controls.length ? (
              i.controls.map((c: Json) => (
                <div className="control-card" key={c.id}>
                  <div>
                    <Badge
                      tone={
                        c.state === "retired"
                          ? "green"
                          : new Date(c.review_due) < new Date()
                            ? "amber"
                            : "neutral"
                      }
                    >
                      {c.state === "retired"
                        ? "Retired"
                        : new Date(c.review_due) < new Date()
                          ? "Review overdue"
                          : "Active"}
                    </Badge>
                    <span className="mono">CONTROL #{c.id}</span>
                  </div>
                  <h3>{c.description}</h3>
                  <p>
                    Review due {date(c.review_due)} · Responsible user #
                    {c.responsible_id}
                  </p>
                  {c.state === "active" &&
                    (user.role === "supervisor" ||
                      c.responsible_id === user.id) && (
                      <button
                        className="secondary"
                        onClick={() =>
                          open("record_control_review", { control_id: c.id })
                        }
                      >
                        Record review
                      </button>
                    )}
                </div>
              ))
            ) : (
              <Empty>No temporary measures recorded.</Empty>
            )}
          </section>
          <section className="panel padded">
            <h2>Closure reviews</h2>
            {i.closure_requests.length ? (
              i.closure_requests.map((r: Json) => (
                <div className="control-card" key={r.id}>
                  <Badge tone={r.status === "approved" ? "green" : "amber"}>
                    {human(r.status)}
                  </Badge>
                  <p>
                    <strong>Evidence reference:</strong> {r.evidence}
                  </p>
                  {r.reason && <p>Decision: {r.reason}</p>}
                  {r.status === "pending" && (
                    <button
                      className="secondary"
                      disabled={user.role !== "supervisor"}
                      title={
                        user.role !== "supervisor"
                          ? "An independent supervisor is required"
                          : ""
                      }
                      onClick={() =>
                        open("review_closure_request", { request_id: r.id })
                      }
                    >
                      Review request
                    </button>
                  )}
                </div>
              ))
            ) : (
              <Empty>
                Closure requires evidence and an independent supervisor review.
              </Empty>
            )}
          </section>
        </div>
        <section className="panel padded timeline">
          <h2>Accountability trail</h2>
          <p className="muted">
            Original records and rejected actions are preserved.
          </p>
          {history.data?.events.map((e: Json) => (
            <div className="timeline-event" key={e.id}>
              <div
                className={
                  "timeline-dot " +
                  (e.action.startsWith("rejected") ? "bad" : "")
                }
              />
              <small>
                {date(e.created_at)} · User #{e.user_id}
              </small>
              <strong>{human(e.action)}</strong>
              {e.after.note && <p>{e.after.note}</p>}
              {e.after.message && <p className="red-text">{e.after.message}</p>}
              <details>
                <summary>Record details</summary>
                <pre>{JSON.stringify(e.after, null, 2)}</pre>
              </details>
            </div>
          ))}
        </section>
      </div>
      {action && (
        <OperationDialog
          name={action.name}
          defaults={action.defaults}
          close={() => setAction(null)}
        />
      )}
    </>
  );
}
function Handovers() {
  const data = useData("get_shift_handover"),
    { user } = useUser();
  const [action, setAction] = useState<Json | null>(null);
  return (
    <>
      <Heading
        eyebrow="SHIFT CONTINUITY"
        title="A handover. Not a reset."
        subtitle="Unresolved work and temporary measures stay visible until their own review is complete."
        action={
          <button
            className="primary"
            onClick={() => setAction({ name: "create_handover" })}
          >
            <Plus size={17} />
            Create handover
          </button>
        }
      />
      <div className="shift-strip">
        {["A / MORNING", "B / EVENING", "C / NIGHT"].map((x, n) => (
          <React.Fragment key={x}>
            <div>
              <span>0{n + 1}</span>
              <strong>{x}</strong>
              <small>Shared operational continuity</small>
            </div>
            {n < 2 && <ArrowRightLeft size={20} />}
          </React.Fragment>
        ))}
      </div>
      <ErrorBox error={data.error} />
      {data.data?.handovers.map((h: Json) => (
        <section className="panel padded" key={h.id}>
          <div className="section-title">
            <div>
              <div className="eyebrow">HANDOVER #{h.id}</div>
              <h2>
                {h.outgoing} <ChevronRight size={17} /> {h.incoming}
              </h2>
            </div>
            <Badge tone={h.acknowledged ? "green" : "amber"}>
              {h.acknowledged
                ? "Receipt acknowledged"
                : "Awaiting acknowledgment"}
            </Badge>
          </div>
          <p>
            {h.incident_ids.length} carried cases · Recipient #{h.recipient_id}{" "}
            · Created {date(h.created_at)}
          </p>
          <div className="case-grid">
            {h.current_incidents.slice(0, 3).map((i: Json) => (
              <CaseCard key={i.id} incident={i} />
            ))}
          </div>
          <details className="handover-all">
            <summary>
              View all {h.current_incidents.length} carried cases
            </summary>
            <IncidentTable incidents={h.current_incidents} />
          </details>
          {!h.acknowledged && (
            <button
              className="primary"
              disabled={h.recipient_id !== user.id}
              title={
                h.recipient_id !== user.id
                  ? "Only the designated recipient can acknowledge"
                  : ""
              }
              onClick={() =>
                setAction({
                  name: "acknowledge_handover",
                  defaults: { handover_id: h.id },
                })
              }
            >
              <Check size={17} />
              Acknowledge receipt
            </button>
          )}
          <p className="muted">
            Acknowledgment confirms receipt. It does not confirm physical safety
            or close an incident.
          </p>
        </section>
      ))}
      {data.data?.handovers.length === 0 && (
        <Empty>No handovers recorded yet.</Empty>
      )}
      {action && (
        <OperationDialog
          name={action.name}
          defaults={action.defaults}
          close={() => setAction(null)}
        />
      )}
    </>
  );
}
function Integrity() {
  const data = useData("get_integrity_flags");
  return (
    <>
      <Heading
        eyebrow="HANDOVER INTEGRITY ENGINE"
        title="Every flag has a reason."
        subtitle="Deterministic checks against recorded responsibilities, review dates and verification."
      />
      <div className="integrity-banner">
        <ShieldCheck size={26} />
        <div>
          <h3>Evidence before assumptions.</h3>
          <p>
            An overdue review means a check is missing. It does not prove that a
            physical safeguard failed.
          </p>
        </div>
        <Badge tone="amber">{data.data?.flags.length ?? "—"} FLAGS</Badge>
      </div>
      <ErrorBox error={data.error} />
      <div className="flag-list">
        {data.data?.flags.map((f: Json, n: number) => (
          <div className="flag" key={n}>
            <AlertTriangle className="amber-text" size={19} />
            <div>
              <span className="eyebrow">{human(f.rule)}</span>
              <p>{f.message}</p>
            </div>
            {f.incident_id && f.incident_id !== "operation" ? (
              <NavLink to={"/incidents/" + f.incident_id} className="text-link">
                {f.incident_id}
                <ArrowUpRight size={16} />
              </NavLink>
            ) : (
              <NavLink className="text-link" to="/handover">
                Handover #{f.handover_id}
                <ArrowUpRight size={16} />
              </NavLink>
            )}
          </div>
        ))}
      </div>
      {data.data?.flags.length === 0 && (
        <Empty>No integrity flags in current records.</Empty>
      )}
    </>
  );
}
function Review() {
  const data = useData("list_open_incidents", "?state=review_pending"),
    { user } = useUser(),
    pending =
      data.data?.incidents.filter((i: Json) => i.state === "review_pending") ||
      [];
  return (
    <>
      <Heading
        eyebrow="INDEPENDENT VERIFICATION"
        title="Close the loop, with evidence."
        subtitle="Inspect evidence, retire temporary measures and record an accountable decision."
      />
      {user.role !== "supervisor" && (
        <div className="info-banner">
          <ShieldCheck size={18} />
          You can view requests. Only an independent supervisor can approve or
          reject them.
        </div>
      )}
      <section className="panel padded">
        <div className="section-title">
          <h2>Pending closure requests</h2>
          <Badge tone="amber">{pending.length} IN VIEW</Badge>
        </div>
        <ErrorBox error={data.error} />
        {pending.length ? (
          <div className="case-grid">
            {pending.map((i: Json) => (
              <CaseCard key={i.id} incident={i} />
            ))}
          </div>
        ) : (
          <Empty>
            No pending requests in the current view. Search Operations for a
            specific case.
          </Empty>
        )}
        <p className="muted">
          Approval requires an accepted owner, no unresolved dispute, retired
          measures, evidence and an independent verification reference.
        </p>
      </section>
    </>
  );
}
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
);

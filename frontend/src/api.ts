export type Json = Record<string, any>;
export async function api(path: string, body?: unknown): Promise<any> {
  const r = await fetch("/api" + path, {
    method: body === undefined ? "GET" : "POST",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CarrySafe-Intent": "interactive",
    },
    body: body === undefined ? undefined : JSON.stringify(body),
    signal: AbortSignal.timeout(120000),
  });
  const data = await r.json();
  if (!r.ok)
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : JSON.stringify(data.detail || data),
    );
  return data;
}
export const human = (s: string) =>
  s.replaceAll("_", " ").replace(/^./, (x) => x.toUpperCase());
export const date = (s: string) =>
  new Date(s).toLocaleString("en-IN", {
    timeZone: "Asia/Kolkata",
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
export function convert(value: string, s: Json): unknown {
  if (value === "")
    return s.anyOf?.some((x: Json) => x.type === "null") ? null : undefined;
  const type = s.type || s.anyOf?.find((x: Json) => x.type !== "null")?.type;
  if (type === "integer" || type === "number") return Number(value);
  if (type === "boolean") return value === "true";
  if (
    s.format === "date-time" ||
    s.anyOf?.some((x: Json) => x.format === "date-time")
  )
    return new Date(value).toISOString();
  return value;
}

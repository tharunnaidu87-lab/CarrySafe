import { describe, it, expect } from "vitest";
import { convert, human } from "./api";
describe("schema-driven consequential forms", () => {
  it("keeps an optional owner unassigned", () =>
    expect(
      convert("", { anyOf: [{ type: "integer" }, { type: "null" }] }),
    ).toBeNull());
  it("does not coerce false into approval", () =>
    expect(convert("false", { type: "boolean" })).toBe(false));
  it("retains version as a number", () =>
    expect(convert("3", { type: "integer" })).toBe(3));
  it("serializes explicit time zone", () =>
    expect(convert("2026-10-23T15:00:00+05:30", { format: "date-time" })).toBe(
      "2026-10-23T09:30:00.000Z",
    ));
  it("shows readable operation labels", () =>
    expect(human("record_control_review")).toBe("Record control review"));
});

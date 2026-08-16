import assert from "node:assert/strict";
import { test } from "node:test";

import { computeStats, parseCsv, renderBadge, renderSvg } from "./worker.mjs";

const HEADER = "#,الموضع,نص الآية,الحكم المذكور,المصدر,صحيح/خطأ,ملاحظات";

function sheet(...verdicts) {
  const lines = [HEADER];
  verdicts.forEach((v, i) =>
    lines.push(`${i + 1},1:1,text,hukm,src,${v},`));
  return lines.join("\r\n");
}

test("parseCsv handles quoted commas, doubled quotes, embedded newlines", () => {
  const rows = parseCsv('a,"b,1","c""q"\r\n"multi\nline",e,');
  assert.deepEqual(rows, [["a", "b,1", 'c"q'], ["multi\nline", "e", ""]]);
});

test("computeStats counts verdicts via the صحيح/خطأ header column", () => {
  const s = computeStats(parseCsv(sheet("صحيح", "صحيح", "خطأ", "فيه وجهان", "", "")));
  assert.equal(s.total, 6);
  assert.equal(s.reviewed, 4);
  assert.equal(s.sahih, 2);
  assert.equal(s.khata, 1);
  assert.equal(s.wajhan, 1);
});

test("computeStats ignores whitespace verdicts and short rows", () => {
  const rows = parseCsv(sheet("صحيح"));
  rows.push(["2", "1:2", "t", "h", "s", "   "]);
  rows.push(["3", "1:3", "t"]);
  const s = computeStats(rows);
  assert.equal(s.total, 3);
  assert.equal(s.reviewed, 1);
});

test("renderSvg shows fraction, breakdown, date", () => {
  const svg = renderSvg(computeStats(parseCsv(sheet("صحيح", "خطأ", ""))), "2026-08-16");
  assert.ok(svg.startsWith("<svg"));
  assert.ok(svg.includes("2 / 3"));
  assert.ok(svg.includes("1 confirmed"));
  assert.ok(svg.includes("1 in adjudication"));
  assert.ok(svg.includes("2026-08-16"));
});

test("renderBadge colors: blue in progress, brightgreen when done+clean", () => {
  const part = JSON.parse(renderBadge(computeStats(parseCsv(sheet("صحيح", "")))));
  assert.equal(part.schemaVersion, 1);
  assert.equal(part.message, "1/2 rulings");
  assert.equal(part.color, "blue");
  const done = JSON.parse(renderBadge(computeStats(parseCsv(sheet("صحيح", "صحيح")))));
  assert.equal(done.color, "brightgreen");
});

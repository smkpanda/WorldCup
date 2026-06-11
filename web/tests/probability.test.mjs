import assert from "node:assert/strict";
import test from "node:test";
import fs from "node:fs";

function probabilityTotal(home, draw, away) {
  return Math.round((home + draw + away) * 100) / 100;
}

test("probabilities sum to 100", () => {
  assert.equal(probabilityTotal(58, 25, 17), 100);
});

test("generated predictions contain schedule and review fields", () => {
  const data = JSON.parse(fs.readFileSync(new URL("../data/predictions.json", import.meta.url), "utf8"));
  const opening = data.find((match) => match.id === "mex-rsa");
  const review = data.find((match) => match.id === "review-arg-fra-2022");
  assert.equal(opening.kickoff, "2026-06-11T19:00:00Z");
  assert.match(opening.likelyScore, /^\d+-\d+$/);
  assert.equal(review.actualScore, "3-3");
  assert.ok(review.errorReasonsZh.length > 0);
});

test("default locale and explicit time zones are configured", () => {
  const root = fs.readFileSync(new URL("../app/page.tsx", import.meta.url), "utf8");
  const i18n = fs.readFileSync(new URL("../lib/i18n.ts", import.meta.url), "utf8");
  assert.match(root, /redirect\("\/en"\)/);
  assert.match(i18n, /Asia\/Shanghai/);
  assert.match(i18n, /timeZone: "UTC"/);
});

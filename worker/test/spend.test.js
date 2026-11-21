// SPDX-License-Identifier: LicenseRef-Ultrastable-USL-1.0
// Copyright (c) 2026 Rowan Brad Quni-Gudzinas. Non-commercial use free; commercial use requires a license. See LICENSE.
// SPEND-SOFT-1 in the seed: soft spend throttle (ported from ultrastable/ultrastable seed/worker/src/spend.js). No band stops essential work.
import test from 'node:test';
import assert from 'node:assert/strict';
import { estimateDay, level, BANDS, spendConfig } from '../src/spend.js';

test('bands get slower as spend rises and never stop', () => {
  let prev = 0;
  for (const s of [0, 0.4, 0.6, 0.8, 1, 5, 1e6]) {
    const r = level({ plan: 'paid', usd_today: s * 5, fixed_usd: 0 }, 5, new Date('2026-11-21T01:00:00Z'));
    assert.ok(BANDS.some(b => b.level === r.level)); assert.ok(Number.isFinite(r.knobs.pace) && r.knobs.pace >= prev); prev = r.knobs.pace;
  }
});
test('free plan bills nothing; target defaults to 5 USD', () => {
  assert.equal(estimateDay({ requests: 1e9 }, { plan: 'free' }).usd_today, 0);
  assert.equal(spendConfig({}, {}).target_usd_day, 5);
});

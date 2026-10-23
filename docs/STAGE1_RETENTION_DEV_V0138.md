# Stage 1 Retention Dev Plan — v0.13.8-dev

## Safety boundary

- Baseline: `v0.13.7 bilingual`
- Baseline branch: `baseline/pre-stage1-retention-v0.13.7`
- Dev branch: `dev/stage1-retention-v0.13.8`
- Main / Production / public GitHub Pages / itch.io: **unchanged**
- Stage 2-10 numeric difficulty values: **unchanged**
- PERFECT logic: **unchanged from the current build**
- Images / bonus videos: **unchanged**

## 1. Telemetry added

Existing events are preserved. New events only add detail.

### stage1_attempt_start

Params:
- `attempt_id`: random per-attempt identifier; not personally identifying
- `attempt_no`: local instrumented attempt counter on this browser
- `first_instrumented_attempt`: true only for the first attempt observed after this instrumentation exists
- `start_source`: new_game / load_save / continue_free / continue_rewarded / direct
- `from_save`
- `input_mode`: keyboard / mobile
- `guard_max_ms`

### stage1_first_capture

Recorded once per Stage 1 attempt:
- elapsed time
- before / after area
- character-mask before / after when available
- input mode
- whether the bounded entry guard was still active

### stage1_first_death

Recorded once per Stage 1 attempt:
- elapsed time
- death reason
- area and progress metric at death
- lives after loss

The existing `life_lost` event remains and gains attempt metadata.

### stage1_clear

Recorded on the first 80% clear per Stage 1 attempt:
- elapsed time
- attempt deaths
- progress metric / value
- area / score

### stage2_entry

Recorded whenever Stage 2 starts:
- start source
- whether it is the first instrumented Stage 2 entry
- previous Stage 1 clear attempt ID when available in the same browser session

### Privacy

No name, email, account ID, advertising ID, precise location, or new device fingerprint is added.
The new `attempt_id` is random and scoped to a gameplay attempt.

## 2. Tutorial change

Required learning steps become:

1. MOVE
2. DRAW THE LINE
3. CONNECT BACK / first successful capture

After the first successful territory capture, the core tutorial completes.

RETRACT is no longer a required interaction. It is shown as an **OPTIONAL TIP** on the ready screen:

- PC: release the mapped CAPTURE key to retreat along the line.
- Mobile: tap CAPTURE again to retreat.
- DASH remains an optional tip.

Existing tutorial start / step / complete / skip events remain compatible. New builds will stop emitting required-step `retract` completion because it is no longer mandatory.

## 3. Stage 1 bounded entry guard

Dev setting:

```js
const STAGE1_ENTRY_GUARD = {
  enabled: true,
  maxMs: 15000,
  bossSpeedScale: 0.82,
  chaseScale: 0.55,
  suppressProjectiles: true,
  postGuardShotDelayMs: 900
};
```

Rules:

- Stage 1 only.
- Ends immediately after the first successful capture.
- Hard upper bound: 15 seconds.
- No invulnerability.
- Boss / minion contact and line-cut danger still exist.
- During the guard, boss movement pressure is reduced and boss projectiles are suppressed.
- After the guard ends, the existing Stage 1 difficulty resumes.
- Stage 2-10 values and behavior are not changed by this guard.

## 4. 80% clear bank prototype

A prototype is implemented behind:

```js
const CLEAR_BANK_V1 = { enabled: false, ... };
```

Therefore **current dev gameplay does not activate it**.

Proposed behavior when later enabled:

1. At 80%, store a small local clear-bank record for the current save slot.
2. The player may choose KEEP PLAYING for 90% / PERFECT.
3. If the player reaches GAME OVER before moving to Stage 2, GAME OVER can offer:
   `NEXT STAGE · CLEAR SAVED`
4. Choosing it restores the banked score/lives snapshot and advances to the next stage.
5. Normal NEXT STAGE clears the temporary bank.

This keeps the risk of losing the current bonus attempt while preventing the already-earned 80% progression from being erased.

### Reason it remains OFF

Before activation we still need product approval on:
- whether lives should restore to the 80% snapshot or always at least 1,
- whether score gained after 80% but before death should be discarded,
- whether the same rule should later apply to Stage 2-9,
- Stage 10 ending behavior.

## 5. Compatibility expectations

- Existing analytics dashboard continues reading `stage_start`, `stage_milestone`, `life_lost`, etc.
- New event names are additive.
- Existing saves do not need migration.
- Key mapping input remains unchanged.
- Mobile CAPTURE lock remains unchanged.
- Stage 2-10 difficulty constants remain unchanged.
- Existing 90% bonus scenes, Gallery, Continue, Collection, BGM and service assets remain unchanged.

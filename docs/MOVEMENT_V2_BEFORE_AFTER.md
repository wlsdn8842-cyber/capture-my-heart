# Movement v2 + Fair Random Spawn — BEFORE / AFTER

## BEFORE baseline
- Version: `v0.13.3 mobile rotation recovery`
- Commit: `d12eed5703b1d0b3891dbb22f1c9b6211bac1f26`
- Preserved branch: `baseline/pre-movement-v2-v0.13.3`

### BEFORE behavior
1. The player could move across any claimed/safe cell, including the interior of already captured territory.
2. Desktop capture remained logically held until Space key-up. If the player kept holding Space and direction after reconnecting, key repeat could re-arm capture immediately.
3. Mobile capture lock already turned off on capture completion, but desktop/mobile did not share one explicit post-capture disarm rule.
4. Boss/minion starting cells used independent random unclaimed-cell picks with player distance, but no explicit enemy-to-enemy separation guarantee.

## AFTER target
- Version: `v0.14.0 movement v2`
- Working branch: `movement-v2-fair-random-spawn-rebased`

### AFTER behavior
1. Safe movement is restricted to claimed cells that touch unclaimed territory — the active capture boundary.
2. Entering unclaimed territory still requires CAPTURE.
3. Reconnecting a line auto-disarms CAPTURE.
   - Desktop: Space must be released before capture can re-arm.
   - Mobile: CAPTURE LOCK automatically switches off.
4. Boss spawn is randomized inside the map with a minimum player distance.
5. Minion spawns are randomized and distributed with both player-distance and enemy-separation constraints.
6. Existing DASH, auto-retract, lives, items, boss skills, stage difficulty, bonus scenes, collection reward, and 3-day collection reopen behavior remain unchanged.

## Rollback rule
If Movement v2 causes a regression, compare against or restore from:
`baseline/pre-movement-v2-v0.13.3`

## Verification
The deployment workflow runs `overrides/verify_movement_v2.js` against the built `game.js` to verify boundary movement, capture auto-off, mobile/desktop behavior, and fair spawn separation.


## Corner traversal hotfix

### BEFORE corner fix
- Version: `v0.14.0 movement v2`
- Commit: `7416286428e6202df01808e92e8231f77f70ee9f`
- Preserved branch: `baseline/pre-corner-fix-v0.14.0`
- Boundary detection used only the four orthogonal neighbors, so some 90-degree/concave corners could become non-traversable.

### AFTER corner fix
- Version: `v0.14.1 corner traversal`
- Boundary detection checks all eight neighboring cells.
- Claimed interior cells with no adjacent unclaimed cell remain blocked.
- Orthogonal boundary movement remains unchanged.
- Claimed corner cells that touch unclaimed territory diagonally are now traversable.

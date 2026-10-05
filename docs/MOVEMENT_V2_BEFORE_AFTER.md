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


## Safe boundary transfer hotfix

### BEFORE safe transfer
- Version: `v0.14.1 corner traversal`
- Commit: `05cfadd048f78cbdb8e9259b1d9b19fbf74c9c08`
- Preserved branch: `baseline/pre-safe-transfer-v0.14.1`
- Boundary-only movement could strand the player on one boundary loop when another playable boundary was separated by already-claimed safe territory.

### AFTER safe transfer
- Version: `v0.14.2 safe boundary transfer`
- Normal movement still follows the active boundary.
- If another boundary exists straight ahead and every cell between is already CLAIMED, the player may cross that safe corridor in a straight line.
- While crossing, perpendicular turns are blocked; the player may continue forward or reverse back to the origin boundary.
- CAPTURE does not start inside the transfer corridor.
- If no boundary exists ahead, claimed interior remains blocked.
- Existing Movement v2 corner traversal and Fair Random Spawn remain unchanged.


## Routed safe path transfer hotfix

### BEFORE routed path
- Version: `v0.14.2 safe boundary transfer`
- Commit: `ba200f851c32868b22240ad8cb4e3225a03a3c2d`
- Preserved branch: `baseline/pre-safe-path-v0.14.2`
- Transfer only worked when another boundary existed on the same straight row/column.
- A boss relocation or asymmetric capture shape could leave the next usable boundary diagonal or around a bend, preventing transfer.

### AFTER routed path
- Version: `v0.14.3 safe path transfer`
- When the player pushes into already-claimed interior from a boundary, the game searches the CLAIMED area with BFS for the nearest different boundary.
- The route can turn through the claimed safe area; it no longer requires row/column alignment.
- Once armed, transfer automatically follows the route until the target boundary is reached.
- The remaining route is rendered as a glowing gold dashed line (`#ffd54a`) with a gold endpoint ring so it is visually distinct from the pink CAPTURE trail and cyan safe boundary.
- If a boss pattern changes the route while transferring, the game attempts a safe reroute and otherwise returns the player to the stored safe origin.
- Existing Movement v2 boundary following, corner traversal, Fair Random Spawn, and capture auto-off remain unchanged.

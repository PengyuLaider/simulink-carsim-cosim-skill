# Failure diagnosis and validation

## Classify before repairing

| Layer | Typical symptom | First useful evidence |
|---|---|---|
| Environment | Missing module/license, wrong binary, cache conflict | Versions, resolution order, license error, runtime paths |
| Model lifecycle | Not loaded, invalid path, wrong session, incomplete stop | Loaded filename/status, dirty state, original stack and completed output |
| Interface | Vehicle reacts in wrong direction or magnitude | Variable order, compiled widths, units, signs, axle/CG transform |
| Interaction/state | No button, wrong target, rejected request | Control geometry, target ID, request/ack, task/decision identity and phase |
| Planner | No path, timeout, feasible candidate never attempted | Search evidence, candidate identity, filtering, budget and body checks |
| Controller | Planned path is valid but tracking fails | Actual/commanded states, saturation, delays, switching and stop dwell |
| Logging | Empty or old result, success without feedback | Actual output object, time series, task identity, recording/storage errors |
| Migration | Local works, extracted copy fails | Public startup, resolved paths, data, binary compatibility, manifest |

Do not erase the original exception with a generic environment message. Preserve failures from before the fix. An invalid test path is a test-tool defect; correct and rerun it without presenting that failed check as a plant result.

## Lessons from the parking case

These are diagnostic patterns, not mandatory features for every task:

- A missing/unreachable confirmation button needs a real size-dependent interaction test. An internal confirm function cannot prove the user can click the production UI.
- Candidate order can exhaust a budget with duplicate or invalid endpoints. Inspect identities and filtering before adding iterations. This may concern survey-route planning, not the parking planner itself.
- A point path can fit while body, overhang or swept turn does not. Validate the reference point and full body appropriate to the project.
- Preview curvature used at the wrong current position can create opposing steering corrections. Compare actual/commanded angle at consistent times.
- Empty feedback can come from recording disabled by storage exhaustion. Fix storage and preserve recording rather than calling the run successful.
- A skipped target needs a stable identity. Display row indexes are not persistent target identities.
- A progress label does not justify a stall. Define task-progress evidence separately from collision avoidance.

## Test layers and permitted conclusions

| Layer | Observable result | What it does not prove |
|---|---|---|
| Static inventory | Source/model/configuration and dependencies identified | Runtime availability or control correctness |
| Compile | Configured plant loads and dimensions resolve | Motion, tracking, task completion |
| Short open loop | Units/signs and bounded vehicle response observed | Full closed-loop stability or safety |
| Closed loop | Actual plant meets chosen criteria | Every interaction or every scenario |
| Production task | Entry/request/model/plant/log chain works | Statistical generalization |
| Fault/recovery | Relevant failure retained and recovery works | Absence of all untested faults |
| Migration | Extracted entry resolves and tested cases execute | All releases/computers compatible |

Use applicable layers; do not require a GUI test for a headless model. For UI work, test visible/enabled control bounds, request delivery, phase transition, selected target and plant movement. Exercise relevant stale requests, pause/resume, stop completion and restart without discarding the prior run.

## Evidence and regression

Preserve source/configuration identity, software versions, scenario/seed, initialization, raw errors, commands and real feedback, timing and outcome. Link charts to actual logs. Keep planned traces, attempted candidates and executed trajectories distinguishable.

Separate pass, algorithm failure, timeout, environment failure, user rejection, interruption and unverified where applicable. A timeout does not prove geometric infeasibility. A user declining a recommendation is not an algorithmic failure.

Freeze limits before testing. Include accuracy, timing, constraints, actuator limits and independent geometry/physics checks appropriate to the task. If a criterion is wrong, document the rationale, revise the contract and repeat acceptance; do not silently weaken limits or drop failing cases.

After focused repair tests, run the entire agreed suite against one frozen source/configuration. Hash relevant source, SLX, configuration, vehicle input and referenced dependencies through an explicitly reviewed inventory. Any change invalidates that suite's claim about the new version. Never stitch passes from different versions or relabel old failures.

If a license, installation, missing input or user-owned active model blocks native testing, finish independent work, preserve the blocked run and state the exact prerequisite. Never bypass licensing, reset a user's session or retry indefinitely.

Development agents can independently review interface, control, UI or tests. Their review is not runtime evidence and they do not become part of the vehicle controller.

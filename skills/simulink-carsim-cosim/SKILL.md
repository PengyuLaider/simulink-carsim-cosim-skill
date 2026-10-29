---
name: simulink-carsim-cosim
license: MIT
description: Build, inspect, debug, and verify Simulink models coupled to an installed CarSim solver. Use for AI生成Simulink模型, 程序化生成SLX, CarSim联合仿真, S-Function接入, model lifecycle errors, real vehicle feedback, regression, and portable co-simulation delivery. Applies to other VehicleSim products only after checking their installed documentation. Not a generic MATLAB scripting or vehicle-data download skill.
---

# Simulink and CarSim Co-simulation

Turn a requested vehicle task into an inspectable model and a verified execution chain. A drawing, a running UI, a successful compile, and a successful closed loop are different claims. Report exactly which one the evidence establishes.

## Establish the target

- Inspect the existing entry point, model dependencies, project instructions, installed MATLAB/Simulink and CarSim releases, architecture, relevant licenses, and the active session. Do useful read-only work before asking for genuinely missing requirements.
- Preserve the user's task and architecture. Vehicle, solver interface, platform, sample rates, thresholds, and test count come from the target project; do not inherit them from an earlier parking example.
- Separate a new implementation from a repair. Reproduce an existing failure with its original settings and preserve its raw evidence before editing an isolated working copy. Do not stop, overwrite, or close an unrelated or unsaved user model.

## Freeze a small engineering contract

Record task stages, expected behavior, initial conditions, selected vehicle parameter provenance, coordinate frame and vehicle reference point, units, signs, actuator interpretation, state/reset/stop behavior, and acceptance criteria.

For the CarSim boundary, record each import/export variable's name, order, width, unit, sign, frame, rate, initialization, and valid range. Distinguish steering-wheel angle from road-wheel angle and model ports from signal-vector widths. Derive the interface from the installed configuration, not a remembered channel count.

Read [modeling-and-interface.md](references/modeling-and-interface.md) for model generation or interface work. Check the installed release documentation and the primary links in [sources.md](references/sources.md) when API or format compatibility matters.

## Generate a model people can inspect

- Use the target release's MATLAB/Simulink APIs to build named subsystems and explicit connections. Put configuration and required source beside the model, and use project-relative runtime paths where supported.
- If the user requires the algorithm to execute in Simulink, connect its production implementation inside the model. MATLAB System, MATLAB Function, Stateflow, and supporting MATLAB source can be appropriate; putting the computation in a UI callback does not meet that requirement.
- Keep generation repeatable without overwriting active work. A rebuild should target a known generated copy, preserve user edits, and fail clearly on a name/path collision. Keep referenced models if the system needs them; do not flatten everything into one opaque block just to produce one SLX.
- Verify the saved model, inspect the actual block connections and readable layout, and retain its builder or a reproducible change record. A screenshot is supporting evidence, not the executable artifact.

## Connect the actual vehicle solver

Use the installed vendor integration or an existing verified example as the starting point. Inspect the configured S-Function, its resolved module path, parameter expression and data dependencies, and the selected import/export setup. Do not invent vendor block-library names or silently replace CarSim with a bicycle model.

Progress in order: environment discovery → compile → short bounded open-loop inputs → small closed loop → full task. The early tests must check dimensions, units, direction, steering, drive/brake response, and feedback timestamps before a complex maneuver.

An open CarSim Browser is a database/editor observation; it does not prove that Simulink called the solver. Keep stubs, replay, and reduced-order plants explicitly labeled in test harnesses and exclude them from native-plant acceptance. No license or solver access means native execution is unverified, not passed.

## Debug the layer that actually failed

Read [debugging-and-validation.md](references/debugging-and-validation.md) when reproducing failures, adding interaction, or designing tests.

- Identify environment, lifecycle, interface, interaction/state, planner, controller, logging, or migration failures separately. Keep the original identifier, stack and task/configuration identity instead of one generic error label.
- Before querying model parameters, confirm the intended model is loaded from the expected file. Search scoped block properties/types rather than relying only on a remembered nested block path. Preserve a dirty model before any operation that could discard it.
- If a UI exists, let it submit requests and display real results. Validate request/acknowledgment, selected target identity, visible/enabled controls, actual model phase and plant response. Do not bypass the real button with an internal function during UI acceptance.
- Distinguish wall-clock planning time, simulated time, and human waiting. Update progress from actual state and counts, not a timer pretending the solver progressed. Diagnose rendering, search, solver and log-storage bottlenecks independently.
- A feasible planned path does not prove tracking. Audit actual feedback, saturation, switching and stopping behavior. Adjust a failing implementation before changing frozen acceptance criteria. A justified criteria change creates a new contract and requires revalidation.

## Verify one version and its evidence

Choose required tests from the user's contract. Include nominal operation, boundary conditions, relevant disturbances, stopping/restarting, and failures/recovery. Interactive projects also require real UI checks. Online-perception claims require observed inputs, not an undisclosed truth map; known-map experiments remain valid when labeled that way.

Preserve configuration/seed, source identity, input data identity, raw errors, actual commands/feedback, timing, failure artifacts, and independent physical/semantic checks appropriate to the task. Missing or empty logs cannot support success. A safe stop is not automatically task completion.

After focused repair tests, freeze all relevant code, SLX, configuration, vehicle data and referenced dependencies; run the complete agreed suite on that version. Any required failure, timeout, unexecuted case, missing evidence or source drift prevents an all-passed release claim. Never stitch passes from different implementations or relabel earlier failures.

Use [scripts/fingerprint.py](scripts/fingerprint.py) for explicit source/data selection and drift checks. It proves file identity only, not physical correctness or authenticity of reported metrics.

## Package and state the limits

Read [packaging.md](references/packaging.md) for migration or public delivery. Preserve rollback and user history, then test the public entry point in a fresh extracted directory. Report compile/migration checks separately from actual closed-loop tests.

Deliver the runnable entry, model(s), necessary source/configuration and redistributable data, test entry and a concise operation/verification note. Omit transient caches and development probes from the runtime root; preserve useful failure history elsewhere rather than deleting it to improve apparent results.

State parameter provenance and remaining assumptions. Fixed-case regression is not a random success rate, finite search is not a global optimum, simulated detections are not real-image perception, and simulation acceptance is not real-vehicle certification.

## Optional helper and completion report

`scripts/model_inventory.m` inventories an already loaded, stopped model without compiling or saving it. It intentionally does not expand masked/library/referenced content. Use it in a working-copy session; inspect uncovered components separately. Treat its output as private diagnostic material unless redacted for sharing.

Conclude with: what changed, actual versions and interface, tests executed and their evidence, unresolved limits, and the exact startup/delivery location. If an environment prerequisite blocks native execution, deliver completed model work and an explicit unverified status; do not retry indefinitely, kill user processes, or manufacture a pass.

# Modeling and interface work

## Inspect before generating

Locate the intended entry point, saved model and required sources. Check loaded model filenames as well as names: two project copies can have the same model name. Installed toolboxes are not evidence that every required license is available. Record actual resolved S-Function paths and distinguish source/MEX location from the vehicle solver and data it loads.

Use a working copy with a task-specific runtime/cache location where the release supports it. Avoid shared solver instances and caches between parallel sessions. Check logging/storage health before diagnosing an empty result as a control failure. Do not disable recording to hide a storage problem.

For a dirty model, a disk copy omits unsaved in-memory edits. Record that difference first. Do not rename, save over or close the original to obtain a copy. Use a verified non-disruptive snapshot procedure or a separate session; if only a disk snapshot is possible, disclose that it excludes unsaved edits and preserve the original session.

The optional `model_inventory` function observes a stopped, already loaded model. Loading a model can execute its callbacks; review unfamiliar content and use an isolated session. The helper does not initialize the project, execute parameter expressions, compile the S-Function, or prove that a library, mask or model-reference dependency is safe.

The helper is tested with MATLAB/Simulink R2024b. Earlier-release compatibility is unverified; skip or adapt the helper if its syntax is unsupported. Use a unique report path per writer: its existing-file guard is not a concurrent-write lock.

## Write the boundary before wiring it

| Field | Required decision |
|---|---|
| Variable | Exact CarSim import/export name and source dataset/configuration |
| Ordering | Vector position, dimension, and grouping into model ports |
| Meaning | Steering wheel/road wheel, torque/force/pressure, absolute/relative state |
| Units | Explicit conversion between solver and controller units |
| Geometry | Frame orientation, yaw sign and reference point, such as rear axle versus CG |
| Timing | Plant step, control period, measurement period, holds/interpolation |
| Lifecycle | Initialization, reset, pause, stop, restart and output availability |
| Range | Actuator bounds and behavior for invalid or unavailable measurements |

A single input port can carry many imports. `get_param(block,'Ports')` gives port counts, not proof of all channel widths. Resolve actual compiled dimensions and variable meanings with the configured solver. If a property is unavailable, record it as unknown until verified.

## Generate readable SLX

Select APIs supported by the installed release. Common operations include `new_system`, `load_system`, `add_block`, `set_param`, connection APIs, `find_system`, `save_system` and `close_system`. `Simulink.connectBlocks` is newer than `add_line`; do not assume it exists in every target release.

Prefer explicit model/subsystem handles and named signal boundaries. Group task logic, controller, safety, actuator conversion, plant, feedback, and recording. Show units and rate transitions where they matter. Use typed buses when their benefits justify the extra definition.

Supporting MATLAB source is not inherently a workaround: a MATLAB System block executing that implementation is different from a GUI performing the computation outside the model.

A builder should resolve a deliberate output location, preserve user edits, discover real library paths, add/configure/connect components, configure timing and recording, then save/reopen/validate the actual artifact. Only rebuild content known to be generated and within the authorized working copy. Do not use `bdclose('all')`, replace an unrelated model, or clear global state as routine cleanup.

## Prove the plant incrementally

Start from the installed vendor example or documented export/link procedure. The exact S-Function name, parameter syntax, SIMFILE/data hierarchy and vehicle export format are version-specific. A PAR/CPAR workflow used in one release is not a universal portability promise.

Before a full maneuver, apply bounded, short inputs appropriate to the selected vehicle and initial conditions. Check actual import interpretation, output ordering, steering sign, drive/brake response, time progression and model completion. A compile at time zero establishes compatibility, not motion.

Define continuity checks appropriate to the rates and dynamics, such as observed displacement versus independently integrated actual velocity plus a justified numeric tolerance. Do not impose a low-speed step limit on higher-speed travel and then loosen all safety rules to make it pass.

Keep safety and progress separate: a valid safety intervention and an incomplete task can coexist. Any state reset, coordinate reinitialization or solver-instance replacement must be deliberate and recorded.

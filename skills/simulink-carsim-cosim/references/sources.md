# Primary documentation

Checked 2026-10-29. Follow the installed target release documentation; current web pages do not establish backward compatibility. These links support APIs/integration concepts, not a universal vehicle interface or performance claim.

| Source | Use |
|---|---|
| [OpenAI Build skills](https://developers.openai.com/plugins/build/skills) | SKILL.md and progressive disclosure |
| [OpenAI Skill discovery](https://learn.chatgpt.com/docs/build-skills) | Local discovery and optional agents/openai.yaml |
| [MathWorks Programmatic Model Editing R2024b](https://www.mathworks.com/help/releases/R2024b/simulink/programmatic-modeling.html) | Release-specific loading, creating, connecting and saving |
| [MathWorks Current Model Editing](https://www.mathworks.com/help/simulink/programmatic-modeling.html) | Compare newer APIs with the installed release |
| [CarSim external integration](https://www.carsim.com/products/supporting/simulink/) | Native S-Functions and configurable import/export variables |
| [VehicleSim Simulink memo](https://www.carsim.com/downloads/pdf/Simulink_ABS_Example.pdf) | Linking example; February 2018 document, not a latest-release guarantee |

This workflow also abstracts lessons from a continuous-perception parking project: wrong-session debugging, unloaded-model callbacks, unreachable controls, route-candidate filtering, recording/storage failures and source-consistent regression. Its original code, measurements, vehicle data and identifying conversation details are not distributed here.

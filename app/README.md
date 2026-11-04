# CrowdScope demonstration

Run `python app/launch.py` from the repository root, or open `app/index.html` directly. The app is self-contained: no CDN, account, backend inference service or network upload is required. Default local address: `http://127.0.0.1:8770/`.

The replay shows **synthetic JuPedSim trajectories**, not recorded human tracks or live detection. Its initial 80 agents pass through a 1.2 m entrance. The underlying development run remains timestep-sensitive; the animation does not validate an evacuation forecast.

Controls let you scrub/play the replay, change the working information representation, budget, assumed prevalence and assumed observation error. Zone density uses usable area; speeds use adjacent past replay samples. Each unit provides capacity for two hypothetical requests. Fixed request rates are 0.1/0.4. Stored observation bits have 20% noise; changing the assumed error does not regenerate them. Optional profile colours display simulation truth, never recognised disability.

The JavaScript allocator uses the same Poisson-binomial expected-shortfall formulation and exhaustive lexicographic allocation search as the Python planner. A separate check compared 100 seeded Python/JavaScript fixtures. `check_planner.cjs` accepts a JSON fixture file with `groups`, `budget`, `capacity` and Python `expected` results.

`demo_data.js` contains only a synthetic replay and its generated profile/observation metadata. The source is the saved `room_w1.2_jitterTrue` development case at dt=0.005 s; frames are sampled every 0.5 s for display. The final empty frame follows the verified all-agent exit ledger. No person-level SiME data is bundled.

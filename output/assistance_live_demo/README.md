# Assistance-link movement demo

Side-by-side playback of freshly recomputed JuPedSim movement with assistance coordination and independent movement. This is a presentation interface for the circular-agent escort approximation in the current paper.

## Open the saved demo

From the repository root, with Python 3 installed:

```bash
python research/assistance/launch_demo.py
```

The launcher opens the browser and serves only this demo folder on the local computer. If port 8766 is busy, it chooses an available port and prints the address. Stop with Ctrl+C. Use `--no-browser` to print the URL without opening a browser.

The saved replay needs **no third-party packages or internet connection**. You can also open `replay.html` directly in a browser; all animation data is embedded in the file. GitHub's file viewer displays the source, so download/clone the repository to run it locally.

## Recompute movement

Install the single root `requirements.txt` in your Python environment, then run:

```bash
python research/assistance/launch_demo.py --regenerate
```

Alternatively, `python research/assistance/run_presentation_demo.py` recomputes `demo_runs.json` and `replay.html` without launching a server. It uses slot 0 from each of the four frozen benchmark layouts, time step 0.005 s, neighbour repulsion 2.6 and zero assumed assistance speed gain. Both threshold coordination and independent modes are rerun, giving eight movement checks. Scientific benchmark outputs are not overwritten. Demo outputs are replaceable presentation exports, not new independent experimental evidence.

## Present it

- Choose either doorway, the mixed queue/staggered merge, or the right-angle turn.
- Left: coordinated helper–client pairs. Right: identical starts, geometry and nominal paces with independent movement.
- Blue C: client; orange H: helper; purple P: other pedestrian.
- Toggle assistance lines, pause/restart, change speed or scrub through time.
- Green dashed line: exit plane; the full nominal circle must cross to count as exited.
- Displayed clearance is measured from the simulated trajectory, not an ML prediction.

All eight displayed reruns passed the engine's movement checks. In the mixed queue the linked/independent times are 14.635/14.490 s; in the turn they are 19.470/18.210 s. Coordination need not improve clearance, especially when no client speed gain is assumed.

This is circular-agent escorting, not physical wheelchair pushing, an empirical helper calibration, or a validated safety tool. No raw human trajectories or participant mappings are included.

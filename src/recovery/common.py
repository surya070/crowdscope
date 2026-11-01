import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORDS = ROOT / "research/recovery"
OUTPUT = ROOT / "output/recovery"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_design():
    frozen = read(RECORDS / "protocol_freeze_v1.json")
    for path, expected in frozen["files"].items():
        if sha(ROOT / path) != expected:
            raise ValueError(f"Frozen recovery artifact changed: {path}")
    cfg = read(ROOT / "configs/recovery_protocol_v1.json")
    amendment = RECORDS / "numerical_amendment_freeze.json"
    if amendment.exists():
        for path, expected in read(amendment)["files"].items():
            if sha(ROOT / path) != expected:
                raise ValueError(f"Numerical amendment changed: {path}")
        cfg = read(ROOT / "configs/recovery_protocol_v1_1.json")
    active = RECORDS / "movement_amendment_freeze.json"
    if active.exists():
        for path, expected in read(active)["files"].items():
            if sha(ROOT / path) != expected:
                raise ValueError(f"Movement amendment changed: {path}")
        cfg = read(ROOT / "configs/recovery_protocol_v1_2.json")
    outflow = RECORDS / "outflow_amendment_freeze.json"
    if outflow.exists():
        for path, expected in read(outflow)["files"].items():
            if sha(ROOT / path) != expected:
                raise ValueError(f"Outflow amendment changed: {path}")
        cfg = read(ROOT / "configs/recovery_protocol_v1_3.json")
    routing = RECORDS / "routing_amendment_freeze.json"
    if routing.exists():
        for path, expected in read(routing)["files"].items():
            if sha(ROOT / path) != expected:
                raise ValueError(f"Routing amendment changed: {path}")
        cfg = read(ROOT / "configs/recovery_protocol_v1_4.json")
    aperture = RECORDS / "aperture_amendment_freeze.json"
    if aperture.exists():
        for path, expected in read(aperture)["files"].items():
            if sha(ROOT / path) != expected:
                raise ValueError(f"Aperture amendment changed: {path}")
        cfg = read(ROOT / "configs/recovery_protocol_v1_5.json")
    phase = RECORDS / "phase_amendment_freeze.json"
    if phase.exists():
        for path, expected in read(phase)["files"].items():
            if sha(ROOT / path) != expected:
                raise ValueError(f"Routing phase amendment changed: {path}")
        cfg = read(ROOT / "configs/recovery_protocol_v1_6.json")
    refined = RECORDS / "refinement_amendment_freeze.json"
    if refined.exists():
        for path, expected in read(refined)["files"].items():
            if sha(ROOT / path) != expected:
                raise ValueError(f"Refinement amendment changed: {path}")
        cfg = read(ROOT / "configs/recovery_protocol_v1_7.json")
    halved = RECORDS / "halving_amendment_freeze.json"
    if halved.exists():
        for path, expected in read(halved)["files"].items():
            if sha(ROOT / path) != expected:
                raise ValueError(f"Final halving amendment changed: {path}")
        cfg = read(ROOT / "configs/recovery_protocol_v1_8.json")
    assistance = RECORDS / "assistance_amendment_freeze.json"
    if assistance.exists():
        for path, expected in read(assistance)["files"].items():
            if sha(ROOT / path) != expected:
                raise ValueError(f"Assistance amendment changed: {path}")
        cfg = read(ROOT / "configs/recovery_protocol_v1_9.json")
    progress = RECORDS / "progress_feedback_amendment_freeze.json"
    if progress.exists():
        for path, expected in read(progress)["files"].items():
            if sha(ROOT / path) != expected:
                raise ValueError(f"Progress-feedback amendment changed: {path}")
        cfg = read(ROOT / "configs/recovery_protocol_v1_10.json")
    pursuit = RECORDS / "pursuit_navigation_amendment_freeze.json"
    if pursuit.exists():
        for path, expected in read(pursuit)["files"].items():
            if sha(ROOT / path) != expected:
                raise ValueError(f"Pursuit-navigation amendment changed: {path}")
        cfg = read(ROOT / "configs/recovery_protocol_v1_11.json")
    return cfg, read(RECORDS / "scenario_manifest_v1.json")


def pilot_directory(cfg):
    return OUTPUT / "pilots" if cfg["version"] in ["recovery-1.0","recovery-1.1","recovery-1.2"] else OUTPUT / "pilots" / cfg["version"]

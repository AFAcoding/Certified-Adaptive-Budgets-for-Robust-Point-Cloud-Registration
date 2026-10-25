"""Write gpu/CAB_GPU_timing_part2.ipynb from the part-1 notebook: the same setup cells (GPU check, token, Drive,
publishing), then SC2-PCR and TurboReg on the six test sets of gpu_bundle_part2.zip (PROTOCOL.md, addendum C)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
nb = json.loads((HERE / "CAB_GPU_timing_part1.ipynb").read_text(encoding="utf-8"))
cells = nb["cells"]


def src(c):
    return "".join(c["source"])


def cell(kind, text):
    c = {"cell_type": kind, "metadata": {}, "source": text.splitlines(keepends=True)}
    if kind == "code":
        c.update(execution_count=None, outputs=[])
    return c


intro = """# CAB: live timing on a GPU, part 2 (PROTOCOL.md, protocol v3, addendum C)

Times SC2-PCR and TurboReg (full budget and the two certified CAB configurations) on the six remaining test sets of addendum C: KITTI raw drives, 3DMatch, 3DLoMatch, KITTI odometry, FCGF 3DMatch and FCGF 3DLoMatch, on the same 300 test pairs per set as the CPU live timing. Nothing is trained here.

**Steps**
1. Upload `gpu_bundle_part2.zip` to the top level of your Google Drive ("My Drive").
2. Choose a GPU runtime: in Colab, *Runtime > Change runtime type > T4 GPU*; in VS Code with the Colab extension, select a Colab **GPU** server as the kernel.
3. *Run all*. The second cell asks for the GitHub token right away and checks it (a fine-grained token restricted to this repository with *Contents: Read and write*; or store it as the Colab secret `GITHUB_TOKEN`). Then everything runs unattended, about 1.5-2.5 hours on a T4.
4. At the end the results are copied to Drive and published to the GitHub repository (`results/gpu/`). Never put the token in this notebook's code.
"""
gpu_check, token, pip, unzip, publish = cells[1], cells[2], cells[3], cells[4], cells[5]
assert "torch.cuda" in src(gpu_check) and "getpass" in src(token) and "def publish" in src(publish)
unzip_src = src(unzip).replace("gpu_bundle_part1", "gpu_bundle_part2")
run = """!cd /content/gpu_bundle_part2 && python -u run_gpu_timing.py --bundle . --estimators sc2,turbo --out /content/cab_gpu_results_sc2_turbo_part2.json
publish("/content/cab_gpu_results_sc2_turbo_part2.json")
"""
nb["cells"] = [cell("markdown", intro), gpu_check, token, pip, cell("code", unzip_src), publish,
               cell("markdown", "## SC2-PCR and TurboReg on the six test sets of part 2\n"), cell("code", run)]
for c in nb["cells"]:
    if c["cell_type"] == "code":
        c["outputs"], c["execution_count"] = [], None
(HERE / "CAB_GPU_timing_part2.ipynb").write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("wrote", HERE / "CAB_GPU_timing_part2.ipynb", len(nb["cells"]), "cells")

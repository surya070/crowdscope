"""Export scientific result figures from the audited frozen comparison only."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from src.recovery.common import ROOT,read
from src.recovery.evaluation import blocks


def main():
    folder=ROOT/"output/compound/comparison_001"
    assert read(folder/"independent_audit.json")["status"]=="passed"
    groups=read(folder/"results.json")
    main=next(g for g in groups if g["variant"]=="main" and g["partition"]=="held_out_geometry_test")
    output=ROOT/"paper/compound/figures";output.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(2,2,figsize=(11,7.5),layout="constrained")
    names=["A","M","F","F_counts","F_no_family","F_no_assistance"]
    labels=["Aggregate","Mobility","Full links","Counts only","No family","No assistance"]
    values=[main["models"][n]["mae"] for n in names]
    ax=axes[0,0]
    ax.bar(range(len(names)),values,color=["#8a949f","#326d9c","#a65043","#8a949f","#8a949f","#8a949f"])
    ax.set_xticks(range(len(names)),labels,rotation=25,ha="right")
    ax.set_ylabel("Mean absolute error (s)")
    ax.set_title("Main held-out test: 24 matched blocks",loc="left",fontsize=11)
    for i,v in enumerate(values):ax.text(i,v+.045,f"{v:.3f}",ha="center",fontsize=8)
    ax.set_ylim(0,max(values)*1.2)
    a=blocks(main["run_metrics"]["M"]);b=blocks(main["run_metrics"]["F"])
    keys=sorted(a)
    ax=axes[0,1]
    for geo,colour in [("G3","#326d9c"),("G4","#8a949f")]:
        positions=[i for i,k in enumerate(keys) if k[0]==geo]
        ax.scatter(positions,[a[keys[i]]-b[keys[i]] for i in positions],s=22,color=colour,label=geo)
    ax.axhline(0,color="#555555",lw=.8)
    ax.set_xlabel("Matched block index within fixed corridors")
    ax.set_ylabel("Mobility MAE minus full-link MAE (s)")
    ax.set_title("Negative values favour mobility alone",loc="left",fontsize=11)
    ax.legend(frameon=False,fontsize=8)
    ax=axes[1,0]
    ordered=[next(g for g in groups if g["variant"]==v and g["partition"]==p) for v,p in [
        ("main","test"),("main","held_out_geometry_test"),("gain_stress","held_out_geometry_test"),("finer_dt","held_out_geometry_test")]]
    x=np.arange(4)
    ax.bar(x-.17,[g["models"]["M"]["mae"] for g in ordered],width=.34,color="#326d9c",label="Mobility")
    ax.bar(x+.17,[g["models"]["F"]["mae"] for g in ordered],width=.34,color="#a65043",label="Full links")
    ax.set_xticks(x,["Same corridor\n8 blocks","Held-out\n24 blocks","Gain stress\n8 blocks","Finer step\n4 blocks"])
    ax.set_ylabel("Mean absolute error (s)")
    ax.set_title("Planned evaluations; different matched subsets",loc="left",fontsize=11)
    ax.legend(frameon=False,fontsize=8)
    ax=axes[1,1]
    corruption=read(folder/"corruption.json")
    values=[main["models"]["M"]["mae"],main["models"]["F"]["mae"]]+[r["mae"] for r in corruption]
    labels=["Mobility reference","Full links, intact","Drop one/type","Rewire one/type"]
    ax.barh(labels,values,color=["#326d9c","#a65043","#8a949f","#8a949f"])
    ax.invert_yaxis();ax.set_xlabel("Mean absolute error (s)")
    ax.set_title("Fixed-model supplied-edge perturbations",loc="left",fontsize=11)
    for i,v in enumerate(values):ax.text(v+.025,i,f"{v:.3f}",va="center",fontsize=8)
    ax.set_xlim(0,max(values)*1.15)
    fig.suptitle("Mobility and relationship information: frozen exploratory comparison",fontsize=14)
    fig.supxlabel("Source: comparison_001 · Synthetic single-lane queues · Conditional on known roster and prescribed routes",fontsize=9)
    fig.savefig(output/"prediction_results.png",dpi=200)
    fig.savefig(output/"prediction_results.svg")
    plt.close(fig)
    print("Saved audited result PNG/SVG; no model fitting.")


if __name__=="__main__":main()

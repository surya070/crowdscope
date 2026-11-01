"""Standalone scientific movement-check figure from saved feasibility outputs."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from src.recovery.common import ROOT, read
from src.compound.cases import cases
from src.compound.movement import footprint


def main():
    folder=ROOT/"output/compound/feasibility_001"
    fig, axes=plt.subplots(2,3,figsize=(13,8.6),layout="constrained")
    chosen=["attached_pair_free","accessible_doorway","inaccessible_doorway","right_angle_turn","mixed_single_lane_queue"]
    labels=["Attached pair: free travel","Pair: accessible 1.0 m doorway","Negative control: 0.60 m doorway","Attached pair: 90° turn","Mixed queue: seven occupants"]
    mapping={c["name"]:c for c in cases()}
    colours={"wheelchair":"#117d75","adult":"#326d9c","adult_parent":"#326d9c","older":"#815e9d","child":"#c08a28"}
    for ax,name,title in zip(axes.flat,chosen,labels):
        case=mapping[name]
        result=read(folder/(name+"__dt0.01__q16.json"))
        area=case["area"]
        geometries=[area] if area.geom_type=="Polygon" else area.geoms
        for part in geometries:
            ax.add_patch(Polygon(list(part.exterior.coords),facecolor="#f2f3f5",edgecolor="#68717c",lw=1))
        unit_by_id={u.id:u for u in case["units"]}
        roster={m.id:m for u in case["units"] for m in u.members}
        for pid,member in roster.items():
            points=[f["positions"][str(pid)] for f in result["frames"] if str(pid) in f["positions"]]
            if points:
                x,y=zip(*points)
                ax.plot(x,y,color=colours.get(member.profile,"#666666"),lw=1,alpha=.8)
        times=([0,3.6,8] if name=="right_angle_turn" else [0,3,5.8] if name!="mixed_single_lane_queue" else [0,4,8])
        if name=="inaccessible_doorway":times=[0,10,40]
        for time in times:
            frame=min(result["frames"],key=lambda f:abs(f["t"]-time))
            for pose in frame["units"]:
                u=unit_by_id[pose["id"]]
                shape=footprint(u,pose=tuple(pose["pose"]))
                ax.add_patch(Polygon(list(shape.exterior.coords),facecolor="#8ea9b8",edgecolor="#375361",alpha=.22,lw=.7))
                for pid,xy in u.centres(*pose["pose"]).items():
                    if str(pid) in frame["positions"]:
                        ax.plot(*xy,"o",ms=3,color=colours.get(roster[pid].profile,"#666666"))
        if case["exit_axis"]==0:
            ax.axvline(case["exit_plane"],color="#a14943",ls="--",lw=1)
        else:
            ax.axhline(case["exit_plane"],color="#a14943",ls="--",lw=1)
        ax.set_title(title,fontsize=11,loc="left")
        ax.set_xlabel("x position (m)");ax.set_ylabel("y position (m)")
        ax.set_aspect("equal",adjustable="datalim")
        ax.autoscale_view()
        status=f"All {result['initial_occupants']} cleared: {result['completion_s']:.2f} s" if result["complete"] else "Both retained at 40 s; no exits"
        ax.text(.02,.98,status,transform=ax.transAxes,va="top",fontsize=8,color="#333333")
    ax=axes.flat[-1]
    positives=[c for c in cases() if c["expected_complete"]]
    for dt,marker,colour in [(.04,"o","#326d9c"),(.02,"s","#a96b30")]:
        delta=[]
        for case in positives:
            fine=read(folder/(case["name"]+"__dt0.01__q16.json"))["completion_s"]
            coarse=read(folder/("{}__dt{}__q16.json".format(case["name"],dt)))["completion_s"]
            delta.append(coarse-fine)
        ax.plot(range(len(positives)),delta,marker=marker,color=colour,label=f"dt={dt:.2f} s")
    ax.axhline(0,color="#666666",lw=.7)
    ax.set_xticks(range(6),["Pedestrian","Wheelchair","Pair","Doorway","Turn","Queue"],rotation=35,ha="right")
    ax.set_ylabel("Clearance difference from dt=0.01 s (s)")
    ax.set_xlabel("Predeclared positive case")
    ax.set_title("Time-step sensitivity: declared fixtures",fontsize=11,loc="left")
    ax.legend(frameon=False,fontsize=8)
    fig.suptitle("Compound-footprint movement feasibility: saved limiting-case checks",fontsize=15)
    fig.supxlabel("Source: feasibility_001, 29 October 2026 · Synthetic prescribed routes; no empirical or prediction validation.\nShaded footprints are selected snapshots; dashed red line is the measurement exit.",fontsize=9)
    fig.savefig(folder/"movement_checks.png",dpi=180)
    fig.savefig(folder/"movement_checks.pdf")
    plt.close(fig)
    print("Saved scientific PNG and PDF; no simulations or prediction fits.")


if __name__=="__main__":main()

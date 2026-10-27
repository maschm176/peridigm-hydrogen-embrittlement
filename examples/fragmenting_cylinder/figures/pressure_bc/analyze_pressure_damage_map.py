# Unrolled damage map (angle x height) at several times, piece census, and by-radial-layer table for the pressure run.
# Run from imperfection_test/pressure_HE30_4pt/:  python3 ../../figures/pressure_bc/analyze_pressure_damage_map.py  (writes figures/pressure_bc/pressure_HE30_unrolled_damage.png)
import numpy as np, netCDF4 as nc
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
def names(d,k): return [bytes(x).split(b"\0")[0].decode() for x in d[k][:].data]
d=nc.Dataset("pipe4pt_HE30_press.e"); en=names(d,"name_elem_var"); nn=names(d,"name_nod_var")
con=np.array(d["connect1"][:]).reshape(-1)-1; t=np.array(d["time_whole"][:])*1e6
X=np.c_[[np.array(d[c][:])[con] for c in("coordx","coordy","coordz")]].T
ge=lambda n,i: np.array(d[f"vals_elem_var{en.index(n)+1}eb1"][i])
gn=lambda n,i: np.array(d[f"vals_nod_var{nn.index(n)+1}"][i])[con]
o=np.argsort(ge("Element_Id",0)); X=X[o]
th=np.arctan2(X[:,1],X[:,0]); h=(X[:,2]-X[:,2].min())/(X[:,2].max()-X[:,2].min()); r=np.hypot(X[:,0],X[:,1])
sp=np.median(cKDTree(X).query(X,k=2)[0][:,1]); tree=cKDTree(X); pairs=tree.query_pairs(1.5*sp,output_type="ndarray")
d0=np.linalg.norm(X[pairs[:,0]]-X[pairs[:,1]],axis=1)
fi=lambda tt:int(np.argmin(abs(t-tt)))
panels=[318,331,345,398]
fig,axs=plt.subplots(1,len(panels),figsize=(15,5),sharey=True,facecolor="#fcfaf8")
for ax,tt in zip(axs,panels):
    i=fi(tt); B=ge("Broken_Bond_Volume_Averaged",i)[o]; W=ge("Weighted_Volume",i)[o]
    U=np.c_[[gn(f"Displacement{a}",i) for a in "XYZ"]].T[o]; P=X+U
    ok=(W[pairs[:,0]]>0)&(W[pairs[:,1]]>0)&(np.linalg.norm(P[pairs[:,0]]-P[pairs[:,1]],axis=1)<1.8*d0)
    pr=pairs[ok]; _,lab=connected_components(coo_matrix((np.ones(len(pr)),(pr[:,0],pr[:,1])),shape=(len(X),len(X))),directed=False)
    sz=np.bincount(lab); sz_alive=np.sort(sz[sz>0])[::-1]
    # exclude W==0 singletons from "pieces" counts? keep all
    ang=np.minimum(((th+np.pi)/(2*np.pi)*24).astype(int),23)
    hb=np.minimum((h*10).astype(int),9)
    grid=np.array([[B[(ang==a)&(hb==b)].mean() for a in range(24)] for b in range(10)])
    rowmean=grid.mean(1); colstd=grid.mean(0).std()
    print(f"t={t[i]:.0f}us meanB={B.mean():.3f} B>0.9={(B>0.9).mean()*100:.1f}% pieces(top5)={sz_alive[:5].tolist()} n>=10={(sz>=10).sum()} isolated(W=0)={(W<=0).mean()*100:.1f}%")
    print("   B by height decile:",np.round(rowmean,2).tolist(),"| std over angle of height-avg B: %.3f"%colstd)
    im=ax.imshow(grid,origin="lower",aspect="auto",cmap="Oranges",vmin=0,vmax=1,extent=[-180,180,0,10]); ax.set_title(f"t = {t[i]:.0f} µs, p ≈ {5e8*t[i]*1e-6/4e-4/1e6:.0f} MPa",fontsize=11); ax.set_xlabel("angle (deg)")
axs[0].set_ylabel("height (cm)"); fig.colorbar(im,ax=axs,label="mean broken-bond fraction",fraction=0.02)
import os; os.makedirs("../../figures/pressure_bc",exist_ok=True)
fig.suptitle("Pressurized pipe (HE_30): broken-bond fraction, unrolled (angle × height)",fontsize=13)
fig.savefig("../../figures/pressure_bc/pressure_HE30_unrolled_damage.png",dpi=140,bbox_inches="tight",facecolor="#fcfaf8")
print("\n--- by radial layer (0=inner .. 3=outer) ---")
lay=np.minimum(((r-0.020)/0.00125).astype(int),3)
for tt in (290,304,318,331,345,398):
    i=fi(tt); B=ge("Broken_Bond_Volume_Averaged",i)[o]; W=ge("Weighted_Volume",i)[o]; E=ge("Equivalent_Plastic_Strain",i)[o]
    U=np.c_[[gn(f"Displacement{a}",i) for a in "XYZ"]].T[o]; ur=U[:,0]*np.cos(th)+U[:,1]*np.sin(th)
    print(f"t={t[i]:.0f}us meanB by layer",[round(B[lay==k].mean(),2) for k in range(4)],"isolated%",[round((W[lay==k]<=0).mean()*100,1) for k in range(4)],"ur(mm)",[round(ur[lay==k].mean()*1e3,1) for k in range(4)],"eqps",[round(E[lay==k].mean(),2) for k in range(4)])

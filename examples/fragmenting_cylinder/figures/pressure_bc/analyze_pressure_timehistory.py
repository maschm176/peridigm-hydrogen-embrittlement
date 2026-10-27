# Time history of the pressurized-pipe run (pressure, wall displacement, damage, plastic strain, max speed).
# Run from imperfection_test/pressure_HE30_4pt/:  python3 ../../figures/pressure_bc/analyze_pressure_timehistory.py
import numpy as np, netCDF4 as nc
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
def names(d,k): return [bytes(x).split(b"\0")[0].decode() for x in d[k][:].data]
d=nc.Dataset("pipe4pt_HE30_press.e"); en=names(d,"name_elem_var"); nn=names(d,"name_nod_var")
con=np.array(d["connect1"][:]).reshape(-1)-1; t=np.array(d["time_whole"][:])*1e6; nf=len(t)
X=np.c_[[np.array(d[c][:])[con] for c in("coordx","coordy","coordz")]].T
ge=lambda n,i: np.array(d[f"vals_elem_var{en.index(n)+1}eb1"][i])
gn=lambda n,i: np.array(d[f"vals_nod_var{nn.index(n)+1}"][i])[con]
o=np.argsort(ge("Element_Id",0)); X=X[o]
r=np.hypot(X[:,0],X[:,1]); th=np.arctan2(X[:,1],X[:,0]); h=(X[:,2]-X[:,2].min())/(X[:,2].max()-X[:,2].min())
inner=r<0.0207; mid=(h>0.4)&(h<0.6)
print("frames",nf,"t range",t[0],t[-1])
print(" t(us) p(MPa) ur_in(um) ur_mid-ratio  meanB  maxB  Bmid  B>0.5% eqps_mean eqps_max maxspeed")
for i in range(0,nf,max(1,nf//28)):
    U=np.c_[[gn(f"Displacement{a}",i) for a in "XYZ"]].T[o]; V=np.c_[[gn(f"Velocity{a}",i) for a in "XYZ"]].T[o]
    ur=U[:,0]*np.cos(th)+U[:,1]*np.sin(th); B=ge("Broken_Bond_Volume_Averaged",i)[o]; E=ge("Equivalent_Plastic_Strain",i)[o]
    print(f"{t[i]:6.0f} {5e8*t[i]*1e-6/4e-4/1e6:6.0f} {ur[inner].mean()*1e6:9.0f} {ur[inner&mid].mean()/ur[inner].mean():8.2f} {B.mean():8.3f} {B.max():5.2f} {B[mid].mean():6.3f} {(B>0.5).mean()*100:6.1f} {E.mean():8.3f} {E.max():8.2f} {np.linalg.norm(V,axis=1).max():8.0f}")

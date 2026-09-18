"""Seat shape parameterization in millimetres; camera parameters are excluded."""
import numpy as np
NAMES=['rear_length','front_length','width_rear','width_mid','width_front','edge_z_rear','edge_z_mid','edge_z_front','base_z_rear','base_z_mid','base_z_front','top_z_rear','top_z_front']
LOWER=np.array([-25,-25,-22,-22,-22,-15,-15,-15,-25,-25,-25,-15,-15],float)
UPPER=np.array([25,25,22,22,22,15,15,15,12,12,12,15,15],float)
def basis(grid):
 g=np.asarray(grid,float);nr,nc,_=g.shape;out=np.zeros((len(NAMES),nr,nc,3));u=np.linspace(0,1,nr)
 weights=np.stack([np.maximum(1-u*2,0),1-abs(u*2-1),np.maximum(u*2-1,0)])
 out[0,:,:,1]=weights[0,:,None];out[1,:,:,1]=weights[2,:,None]
 for k,w in enumerate(weights):
  for j in range(nr):
   out[2+k,j,:,0]=w[j]*g[j,:,0]/g[j,:,0].max()
   out[5+k,j,:,2]=w[j]*np.array([0,.1,.6,1,0,0])
   out[8+k,j,:,2]=w[j]*np.array([0,0,0,0,1,1])
 for k,w in enumerate([weights[0],weights[2]]):out[11+k,:,:,2]=w[:,None]*np.array([1,1,1,1,0,0])[None,:]
 return out
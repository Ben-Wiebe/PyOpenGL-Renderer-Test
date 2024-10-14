import numpy as np
import time
import struct

from pyrr import Vector3, vector
from opensimplex import OpenSimplex
noise_gen = OpenSimplex(seed=1234)

OFFSET = [np.random.randint(-500, 500) for i in range(3)]

Y_SCALE = 5
X_SCALE = 5

def height_at(nx,  ny):
    s = [0.8, 2, 3.7, 256, 64]
    s2 = [0.367, 2.491, 3.7, 64, 512]
    persistence, lac, exp, height, sample_size = s

    settings = [2**-persistence, 1, 1, 0, 0, 16]
    g, amp, freq, normalization, total, octaves = settings

    scale = 5

    for i in range(octaves):
        noise_value = noise((nx/scale)/sample_size * freq,
                            (ny/scale)/sample_size * freq)
        total += noise_value * amp
        normalization += amp
        amp *= g
        freq *= lac
    total /= normalization
    
    return (total ** exp) * height

def noise(nx, ny):
    return noise_gen.noise2(nx, ny)*0.5+0.5

def norm(vectors):
    a, b, c = vectors
    vx = b[0]-a[0]
    vy = b[1]-a[1]
    vz = b[2]-a[2]
    wx = c[0]-a[0]
    wy = c[1]-a[1]
    wz = c[2]-a[2]
    nx = (vy*wz) - (vz*wy)
    ny = (vz*wx) - (vx*wz)
    nz = (vx*wy) - (vy*wx)
    return (nx, ny, nz)

def normalize(v):
    length = np.sqrt( v[0]**2 + v[1]**2 + v[2]**2 )
    if length == 0: return (0, 0, 0)
    return ( v[0] / length, v[1] / length, v[2] / length )



class Vertex:
    def __init__(self, pos, v_id):
        self.pos = pos
        self.norm = Vector3([0.0,0.0,0.0])
        self.texcoords = [0.0,0.0]
        self.id = v_id
        self.tex_data = [0.0,0.0,0.0]


class TerrainGenerator:
    def __init__(self, gs, pos, step_size=1):
        self.grid_size = gs
        self.pos = pos
        self.step = step_size
        self.indices = 0

    def generate_chunk(self):
        vert_list = []
        st = time.time()

        #################################################################
        # Vertex Generation                                             #
        #################################################################
        
        verts = {}
        max_height = 0
        current_id = 0
        
        s = self.step
        i = 0; j = 0
        while i < self.grid_size+s:
            while j < self.grid_size+s:
                height = height_at(i + self.pos[0], j + self.pos[1])*Y_SCALE
                verts[(i+self.pos[0], j+self.pos[1])] = Vertex([(i+self.pos[0])*X_SCALE, height, (j+self.pos[1])*X_SCALE], current_id)
                if height > max_height: max_height = height
                current_id += 1

                j += s

            i += s
            j = 0
        
##        for i in range(-self.grid_size-1,self.grid_size+1):
##            for j in range(-self.grid_size-1,self.grid_size+1):
##                
##                height = height_at(i, j)*Y_SCALE
##                verts[(i,j)] = Vertex([i*X_SCALE,height,j*X_SCALE], current_id)
##                if height > max_height: max_height = height
##                current_id += 1

        #################################################################
        # Tesselation Steps                                             #
        #################################################################
        
        n = 0
        max_n = (self.grid_size*2) ** 2
        for (i,j), vert in verts.items():
            #print(i+s, j+s)
            if i+s > self.pos[0] + self.grid_size or j+s > self.pos[1] + self.grid_size: continue
            elif i < self.pos[0] or j < self.pos[1]: continue
            V = []
            V.append( verts[(i,j)].pos )
            V.append( verts[(i+s,j)].pos )
            V.append( verts[(i,j+s)].pos )
            V.append( verts[(i+s,j+s)].pos )
            
            N = []
            N.append([norm( (V[0],V[2],V[1]) )])
            N.append([norm( (V[1],V[2],V[3]) )])

            verts[(i,j)].norm += Vector3(N[0])
            verts[(i+s,j)].norm += Vector3(N[0]) + Vector3(N[1])
            verts[(i,j+s)].norm += Vector3(N[0]) + Vector3(N[1])
            verts[(i+s,j+s)].norm += Vector3(N[1])

##                # tex_data: normalized height, N/A, N/A
##                # tex noise: marbling to distort the blending altitude
##                tex_noise = (noise_gen.noise2d(i/12, j/12)/8) + (noise_gen.noise2d(i/5, j/5)/15)
##
##                verts[(i,j)].tex_data += Vector3([V[0][1]/max_height+tex_noise, 0, 0])
##                #verts[(i,j)].tex_data += Vector3([V[0][1]/max_height, 0, 0])

            steps = max_n//10
            percentage = n/max_n*100
            #if not n%steps: print(f"{ round(percentage) }% at { time.time()-st } seconds")
            n += 1

        for v in verts:
            vert = verts[v]
            vert.texcoords = list(v)
            vert_list.extend([*vert.pos, *normalize(vert.norm), *vert.texcoords])

        
        
        #################################################################
        # Index Generation                                              #
        #################################################################
        
        indices = []
        for (i,j), vert in verts.items():
            if i+s > self.pos[0] + self.grid_size or j+s > self.pos[1] + self.grid_size: continue
            elif i < self.pos[0] or j < self.pos[1]: continue
            v = [ verts[(i,j)].id,      verts[(i+s,j)].id,
                  verts[(i,j+s)].id,    verts[(i+s,j+s)].id ]
            indices.extend([v[0], v[1], v[2]])
            indices.extend([v[1], v[3], v[2]])

        #print(indices)
        #input()
        #for v in range(len(vert_list)//12):
        #    for i in range(12*v, 12*v + 12):
        #        print(vert_list[i], end=", ")

        #    print()

        print(indices)

        self.indices = len(indices)
        
        vertices = np.array(vert_list, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)

        print("generated in: " + str(time.time()-st))

        return vertices, indices


if __name__ == "__main__":
    generator = TerrainGenerator(16, (0, 0))
    byte_data, indices = generator.generate_chunk()


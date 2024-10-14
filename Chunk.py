from OpenGL.GL import *

from terrain_generation import *

class Chunk:

    chunk_size = 64

    indices = []

    for y in range(chunk_size-1):
        for x in range(chunk_size-1):
            indices.extend([x + (y*chunk_size),
                            x+chunk_size + (y*chunk_size),
                            x+(chunk_size+1) + (y*chunk_size),
                            x+(chunk_size+1) + (y*chunk_size),
                            x+1 + (y*chunk_size),
                            x + (y*chunk_size)])
    #print([i for i in indices][:60])
    indices = np.array([i for i in indices], dtype=np.uint32)

    verts = []
    for x in range(chunk_size):
        for y in range(chunk_size):
            verts.extend([x/(chunk_size-1), y/(chunk_size-1)])
    #print(verts[:(64*2) + 8])
    verts = np.array(verts, dtype=np.float32)

    def __init__(self, size, pos, depth, chunk_gen):
        self.size = size
        self.pos = pos
        self.depth = depth
        self.children = []

        self.chunk_gen = chunk_gen
        self.generator = TerrainGenerator(size, self.pos, size/64)

        self.heightmap = None
        self.normalmap = None
        self.vao = None
        self.vbo = None
        self.ebo = None

    def generate_vao(self):
        #self.chunk_gen.generate(64, (1110,1110), 1)
        self.heightmap, self.normalmap = self.chunk_gen.generate(self.size, (self.pos[0], self.pos[1]), self.size/64)
        #verts = self.generator.generate_chunk()
        verts = self.verts
        indices = self.indices

        vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)
        ebo = glGenBuffers(1)

        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

        #glEnableVertexAttribArray(1)
        #glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

        #glEnableVertexAttribArray(2)
        #glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))

        self.vao = vao
        self.vbo = vbo
        self.ebo = ebo

    def cleanup_vao(self):
        glDeleteBuffers(1, self.vbo)
        glDeleteBuffers(1, self.vao)
        glDeleteBuffers(1, self.ebo)
        glDeleteTextures(1, self.heightmap)
        glDeleteTextures(1, self.normalmap)

        self.vbo = None
        self.vao = None
        self.ebo = None
        self.heightmap = None
        self.normalmap = None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.pos == other.pos and self.size == other.size and self.depth == other.depth:
                return True

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

from OpenGL.GL import *

from Chunk import *
import time

def distance(p1, p2):
    x1, y1 = p1; x2, y2 = p2
    return ((y2-y1)**2 + (x2-x1)**2)**0.5

class Quadtree:
    
    def __init__(self, camera, chunk_gen, base_size=16384):
        self.chunks = []
        self.num_subdivisions = 8
        self.chunk_gen = chunk_gen
        self.main_node = Chunk(base_size, (-base_size/2, -base_size/2), 0, self.chunk_gen)
        self.main_node.generate_vao()

        #self.current_chunks = []

        #self.generate_base_quadtree()
        self.compute_chunks( (0, 0) )

    def compute_chunks(self, pos):
        st = time.time()
        
        old_chunks = dict(self.chunks)
        self.chunks = {}
        
        chunks_to_do = [self.main_node]
        while chunks_to_do:
            chunk = chunks_to_do[0]
            px, py = pos
            cx, cy = chunk.pos
            chunk_centre = (cx + (chunk.size/2), cy + (chunk.size/2))
            if distance(pos, chunk_centre) < chunk.size * 1.3:
                if chunk.depth < self.num_subdivisions:
                    #if chunk in self.chunks.values(): self.chunks[(chunk.pos[0], chunk.pos[1], chunk.size)]
                    
                    top_left = Chunk(chunk.size/2, (cx, cy), chunk.depth + 1, self.chunk_gen)
                    top_right = Chunk(chunk.size/2, (cx + (chunk.size/2), cy), chunk.depth + 1, self.chunk_gen)
                    bottom_left = Chunk(chunk.size/2, (cx, cy + (chunk.size/2)), chunk.depth + 1, self.chunk_gen)
                    bottom_right = Chunk(chunk.size/2, (cx + (chunk.size/2), cy + (chunk.size/2)), chunk.depth + 1, self.chunk_gen)


                    c = [(top_left.pos[0], top_left.pos[1], top_left.size),
                         (top_right.pos[0], top_right.pos[1], top_right.size),
                         (bottom_left.pos[0], bottom_left.pos[1], bottom_left.size),
                         (bottom_right.pos[0], bottom_right.pos[1], bottom_right.size)]

                    #if old_chunks.get(c[0]):
                    #    top_left = old_chunks.get(c[0])
                    #else:
                    #    top_left.generate_vao()

                    #if old_chunks.get(c[1]):
                    #    top_right = old_chunks.get(c[1])
                    #else:
                    #    top_right.generate_vao()

                    #if old_chunks.get(c[2]):
                    #    bottom_left = old_chunks.get(c[2])
                    #else:
                    #    bottom_left.generate_vao()

                    #if old_chunks.get(c[3]):
                    #    bottom_right = old_chunks.get(c[3])
                    #else:
                    #    bottom_right.generate_vao()

                    chunks_to_do.extend([top_left, top_right, bottom_left, bottom_right])

                    self.chunks[(top_left.pos[0], top_left.pos[1], top_left.size)] = top_left
                    self.chunks[(top_right.pos[0], top_right.pos[1], top_right.size)] = top_right
                    self.chunks[(bottom_left.pos[0], bottom_left.pos[1], bottom_left.size)] = bottom_left
                    self.chunks[(bottom_right.pos[0], bottom_right.pos[1], bottom_right.size)] = bottom_right

                    chunk.children = [top_left, top_right, bottom_left, bottom_right]

            chunks_to_do.remove(chunk)

        for i, chunk in self.chunks.items():
            if chunk.children:
                pass
            else:
                chunk.generate_vao()

        print(f"finished building chunks in {round(time.time()-st)} seconds.")


    def get_chunks_to_do(self, pos):
        chunks = []
        px, py = pos

        for i, chunk in self.chunks.items():
            cx, cy = chunk.pos
            chunk_centre = (cx + (chunk.size/2), cy + (chunk.size/2))

            if distance(pos, chunk_centre) < chunk.size:
                if not chunk.vao:
                    chunk.generate_vao()



            elif distance(pos, chunk_centre) > chunk.size * 3:
                chunk.cleanup_vao()

    def generate_visible(self, pos):

        px, py = pos
        chunks = []



    def generate_base_quadtree(self):

        chunks = {}
        chunks_to_do = [self.main_node]

        while chunks_to_do:
            current_chunk = chunks_to_do[0]
            if current_chunk.depth < self.num_subdivisions:

                top_left = Chunk(current_chunk.size/2, (cx, cy), current_chunk.depth + 1, self.chunk_gen)
                top_right = Chunk(current_chunk.size/2, (cx + (current_chunk.size/2), cy), current_chunk.depth + 1, self.chunk_gen)
                bottom_left = Chunk(current_chunk.size/2, (cx, cy + (current_chunk.size/2)), current_chunk.depth + 1, self.chunk_gen)
                bottom_right = Chunk(current_chunk.size/2, (cx + (current_chunk.size/2), cy + (current_chunk.size/2)), current_chunk.depth + 1, self.chunk_gen)


                c = [(top_left.pos[0], top_left.pos[1], top_left.size),
                        (top_right.pos[0], top_right.pos[1], top_right.size),
                        (bottom_left.pos[0], bottom_left.pos[1], bottom_left.size),
                        (bottom_right.pos[0], bottom_right.pos[1], bottom_right.size)]
            
                chunks_to_do.extend([top_left, top_right, bottom_left, bottom_right])

                self.chunks[c[0]] = top_left
                self.chunks[c[1]] = top_right
                self.chunks[c[2]] = bottom_left
                self.chunks[c[3]] = bottom_right

                chunk.children = [top_left, top_right, bottom_left, bottom_right]
            

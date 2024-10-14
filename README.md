# PyOpenGL-Renderer-Test
A little OpenGL stuff in Python. It's a few years old, and was put together as I was first learning OpenGL concepts. The files are as-is from 2021, except for a few shader things that I toyed around with slightly.

Should be run through main.py. The program generates and renders a large terrain by quadtree, and a skybox. By default, it opens a 1280x720 pixel window, and treats the user's screen as if it were 1920x1080. These can both be changed at the top of 'main.py'.

The terrain is generated using compute shader calls for each leaf of the quadtree. The quadtree isn't inherently dynamic at this point, but the user can press the 'L' key while running it to regenerate the whole tree centred around the camera's position, so you can still see the resolution at any point. Camera movement is controlled using the standard "WASD" for translation, as well as tracking mouse movements for rotation. You can also hold down the 'R' key to display the scene as a wireframe. Textures/Colours on the terrain are mixed at run-time based on the steepness of the terrain, ie. flat regions are grassy, steep regions are rocky, high elevation ones are snowy. There is a depth fog effect rendered over this as well.

The skybox is a simple cubemap rendered behind the terrain.

More specific terrain generation stuff:

  Instead of streaming in/out vertices from the GPU in my terrain generation compute shader (compute_test.glsl), I write the vertex positions to a 2D texture, and do the same for the vertex normals. Every chunk has a texture for both normal and height maps, and every one of these textures is the same size, no matter the resolution of the chunk re. the quadtree. Therefore, vertices and indices for these are created in the Chunk class (Chunk.py), and can be reused for each chunk. The vertices simply point to the location on the heightmap/normal texture that stores the real vertex positions/normals, and of course, the indices dictate the order in which the heightmap is triangulated.

This is a sample of how the terrain may look, with the quadtree origin being the highest resolution (as seen in the wireframe below):
![image](https://github.com/user-attachments/assets/a29e4231-afae-465f-8ab8-817cfe344703)

![image](https://github.com/user-attachments/assets/e87dddce-323f-4f47-8b27-4080c1c8cd24)
These demonstrate the way that the chunks are generated, and the quadtree is subdivided.

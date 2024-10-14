#version 430
#extension GL_ARB_compute_shader : enable
#extension GL_ARB_shader_image_load_store : enable

layout (binding = 0, rgba32f) uniform writeonly image2D heightmap;
layout (binding = 1, rgba32f) uniform writeonly image2D normalmap;

layout(local_size_x=1, local_size_y=1) in;


const float persistence = 0.8;
const float lacunarity = 1.8;
const float exponentiation = 1;//3.4 is nicer, but has issues relating to lower height values
const float height = 2048;
const float sample_size = 5096*4;
const vec2 sample_offset = vec2(0,0);
const float G = pow(2, -persistence);
const int octaves = 50;


//const float sample_size = 5096*4;
//const float height = 2048;


/* other settings
const float persistence = 0.5;
const float lacunarity = 2.0;
const float exponentiation = 5.9;
const float height = 2048;
const float sample_size = 5096*4;
const vec2 sample_offset = vec2(0, 0);
const float G = pow(2, -persistence);
const int octaves = 12;
*/

uniform float chunk_x;
uniform float chunk_y;
uniform float chunk_size;
uniform float step_size;
uniform float sobel_strength;

vec3 permute(vec3 x) { return mod(((x*34.0)+1.0)*x, 289.0); }

float snoise(vec2 v){
	v = v + sample_offset;
	const vec4 C = vec4(0.211324865405187, 0.366025403784439,
           -0.577350269189626, 0.024390243902439);
	vec2 i  = floor(v + dot(v, C.yy) );
	vec2 x0 = v -   i + dot(i, C.xx);
	vec2 i1;
	i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
	vec4 x12 = x0.xyxy + C.xxzz;
	x12.xy -= i1;
	i = mod(i, 289.0);
	vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0 ))
	+ i.x + vec3(0.0, i1.x, 1.0 ));
	vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy),
		dot(x12.zw,x12.zw)), 0.0);
	m = m*m ;
	m = m*m ;
	vec3 x = 2.0 * fract(p * C.www) - 1.0;
	vec3 h = abs(x) - 0.5;
	vec3 ox = floor(x + 0.5);
	vec3 a0 = x - ox;
	m *= 1.79284291400159 - 0.85373472095314 * ( a0*a0 + h*h );
	vec3 g;
	g.x  = a0.x  * x0.x  + h.x  * x0.y;
	g.yz = a0.yz * x12.xz + h.yz * x12.yw;
	return 130.0 * dot(m, g);
}

float height_at(vec2 pos)
{
	float total = 0;
	float normalization = 0;
	
	float amplitude = 1.0;
	float frequency = 1.0;
	
	for (int i = 0; i < octaves; i++)
	{
		float noise_value = snoise((pos/sample_size) * frequency);
		total += noise_value * amplitude;
		normalization += amplitude;
		amplitude *= G;
		frequency *= lacunarity;
	}
	total /= normalization;
	
	float final = pow(total, exponentiation) * height;
	return final;
}

vec3 norm(vec3 a, vec3 b, vec3 c)
{
    float vx = b.x-a.x;
    float vy = b.y-a.y;
    float vz = b.z-a.z;
    float wx = c.x-a.x;
    float wy = c.y-a.y;
    float wz = c.z-a.z;
    float nx = (vy*wz) - (vz*wy);
    float ny = (vz*wx) - (vx*wz);
    float nz = (vx*wy) - (vy*wx);
    return vec3(nx, ny, nz);
}

void main()
{	
	// the invocation - used to draw to the right pixel
	ivec2 invocation = ivec2(gl_GlobalInvocationID.xy);

	float x = float(invocation.x) * step_size;
	float y = float(invocation.y) * step_size;

	float cx = x + chunk_x;
	float cy = y + chunk_y;

	float vert_height = height_at( vec2( cx, cy ) );

	vec3 current_vert = vec3(cx, vert_height, cy);

	vec3 verts[9];

	int i = 0;
	for (int nx = -1; nx < 2; nx++) {

		float step_x = nx*step_size;

		for (int ny = -1; ny < 2; ny++) {

			float step_y = ny*step_size;

			float proper_x = cx + step_x;
			float proper_y = cy + step_y;

			verts[i] = vec3(proper_x, height_at(vec2(proper_x, proper_y)), proper_y);
			i++;
		}
	}

	vec3 normal = vec3(0, 0, 0);

	vec3 norms[6] = {
		norm(verts[1], verts[4], verts[3]),
		norm(verts[4], verts[6], verts[3]),
		norm(verts[4], verts[7], verts[6]),
		norm(verts[2], verts[4], verts[1]),
		norm(verts[2], verts[5], verts[4]),
		norm(verts[5], verts[7], verts[4])
	};

	for (i = 0; i < 6; i++)
	{
		normal += norms[i];
    }
	/*
	normal.y = 1.0/(sobel_strength+0.0001);
	normal.x = (verts[6].y + 2.0 * verts[7].y + verts[8].y) - (verts[0].y + 2.0 * verts[1].y + verts[2].y);
	normal.z = (verts[2].y + 2.0 * verts[5].y + verts[8].y) - (verts[0].y + 2.0 * verts[3].y + verts[6].y);
	*/
	imageStore(heightmap, invocation, vec4(vec3(cx, vert_height, cy), 1.0));
	// for sobel filter
	//imageStore(normalmap, invocation, vec4((normalize(normal)+1)/2, 1.0));
	// for normal mapping
	imageStore(normalmap, invocation, vec4(normalize(normal), 1.0));
}
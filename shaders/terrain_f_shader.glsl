# version 330

in vec3 v_vert;
in vec3 v_norm;
in vec2 v_text;
in float v_dist;

out vec4 out_color;

uniform vec3 Light;
uniform sampler2D grass_texture;
uniform sampler2D stone_texture;
uniform sampler2D snow_texture;
uniform float snow_factor;

const float snow_start_height = 1200;

const vec3 sky_colour = vec3(214, 250, 255)/255;//vec3(0.9, 0.9, 0.9);
const float z_near = 1;
const float z_far = 15000;
const float sight_range = 1.5;

vec3 permute(vec3 x) { return mod(((x*34.0)+1.0)*x, 289.0); }

float snoise(vec2 v){
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

float fog_factor(float distance) {
	return -0.0002/sight_range*(distance-z_far/10*sight_range) + 1;
}

void main()
{
	vec4 grass_texel = texture(grass_texture, v_text);
	vec4 stone_texel = texture(stone_texture, v_text);
	vec4 snow_texel = texture(snow_texture, v_text);

	vec3 norm = (v_norm+1)/2;
	
	float up_factor = dot(normalize(norm), vec3(0.0, 1.0, 0.0));
	
    float lum = clamp(dot(normalize(Light-v_vert), normalize(norm)), 0.0, 1.0) * 0.8 + 0.2;
    vec4 colour = vec4(0,0,0,0);
	
	if (up_factor > snow_factor) {
		if (v_vert.y > (snow_start_height + (snoise(vec2(v_vert.x, v_vert.z)/16) * 16 ))) {
			colour = vec4(snow_texel.rgb*lum, 1.0);
		} else {
			colour = vec4(grass_texel.rgb*lum, 1.0);
		}
	} else {
		colour = vec4(stone_texel.rgb*lum, 1.0);
	}
	//out_color = vec4(v_norm, 1.0);
	out_color = mix(vec4(sky_colour, 1.0), colour, clamp(fog_factor(v_dist), 0, 1));
}

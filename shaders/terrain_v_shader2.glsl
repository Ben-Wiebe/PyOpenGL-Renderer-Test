# version 330

layout(location = 0) in vec2 in_vert;

uniform mat4 model; // combined translation and rotation
uniform mat4 view;
uniform mat4 projection;

uniform sampler2D heightmap;
uniform sampler2D normalmap;

out vec3 v_vert;
out vec3 v_norm;
out vec2 v_text;
out float v_dist;

void main()
{
	vec4 vert = texture(heightmap, vec2(in_vert.x, in_vert.y));
	vec4 norm = texture(normalmap, vec2(in_vert.x, in_vert.y));
	
	norm.x = norm.x * 2 - 1;
	norm.y = norm.y * 2 - 1;
	norm.z = norm.z * 2 - 1;
	
	vec4 pos_relative_to_cam = view * model * vert;
    gl_Position = projection * view * model * vert;
    v_vert = vert.xyz;
    v_norm = norm.xyz;
    v_text = vert.xz/4;
	
	v_dist = length(pos_relative_to_cam.xyz);
}

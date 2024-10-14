# version 330

layout(location = 0) in vec3 in_vert;

uniform mat4 view;
uniform mat4 projection;

out vec3 v_text;

void main()
{
	vec4 position = projection * view * vec4(in_vert, 1.0);
    gl_Position = position.xyww;
    v_text = in_vert;
}

# version 330

in vec3 v_text;
uniform samplerCube cubemap;
uniform vec3 fog_colour;

out vec4 out_color;


const float upper_limit = 25.0;
const float lower_limit = 5.0;


void main()
{    
    vec4 colour = texture(cubemap, v_text);
	float factor = (v_text.y - lower_limit) / (upper_limit - lower_limit);
	factor = clamp(factor, 0.0, 1.0);
	
	//out_color = mix(vec4(fog_colour, 1.0), colour, factor);
	out_color = colour;
}

shader_type spatial;

uniform vec4 stone_color_1 : source_color = vec4(0.85, 0.82, 0.78, 1.0);
uniform vec4 stone_color_2 : source_color = vec4(0.72, 0.69, 0.64, 1.0);
uniform vec4 grout_color : source_color = vec4(0.28, 0.25, 0.22, 1.0);
uniform float tile_size = 2.5;
uniform float grout_width = 0.035;

void fragment() {
	vec2 uv_scaled = UV * (60.0 / tile_size);
	vec2 f = fract(uv_scaled);
	vec2 id = floor(uv_scaled);

	// Grout border detection
	float gx = smoothstep(0.0, grout_width, f.x) * smoothstep(0.0, grout_width, 1.0 - f.x);
	float gy = smoothstep(0.0, grout_width, f.y) * smoothstep(0.0, grout_width, 1.0 - f.y);
	float tile_mask = gx * gy;

	// Checkered Greek flagstone pattern
	float check = mod(id.x + id.y, 2.0);
	vec3 base_tile = mix(stone_color_1.rgb, stone_color_2.rgb, check);

	// Subtle pseudo-noise per tile
	float hash = fract(sin(dot(id, vec2(12.9898, 78.233))) * 43758.5453);
	base_tile *= (0.92 + hash * 0.16);

	ALBEDO = mix(grout_color.rgb, base_tile, tile_mask);
	ROUGHNESS = mix(0.95, 0.5, tile_mask);
}

#ifdef GL_ES
precision mediump float;
precision mediump int;
#endif


uniform sampler2D img;
uniform int channelNum;
uniform float fadeAlpha;

varying vec4 vertTexCoord;

void main() {
  vec4 c = texture(img, vertTexCoord.st);

  // get the color value for the specified channel
  float rgb = (
    (int(channelNum == 0) * c.r) + (int(channelNum == 1) * c.g) + 
    (int(channelNum == 2) * c.b) + (int(channelNum == 3) * c.a)
  );

  gl_FragColor = vec4(rgb, rgb, rgb, fadeAlpha);
}

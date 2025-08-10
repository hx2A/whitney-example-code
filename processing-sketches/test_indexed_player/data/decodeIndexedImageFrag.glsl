#ifdef GL_ES
precision mediump float;
precision mediump int;
#endif


uniform sampler2D img;
uniform float[256] reds;
uniform float[256] greens;
uniform float[256] blues;
uniform int channelNum;
uniform float fadeAlpha;

varying vec4 vertTexCoord;

void main() {
  // this texel code is here because indexing needs to land on one pixel
  ivec2 texSize = textureSize(img, 0);
  ivec2 floorCoord = ivec2(floor(vertTexCoord.st * vec2(texSize - 1)));
  ivec2 ceilCoord = ivec2(ceil(vertTexCoord.st * vec2(texSize - 1)));

  vec4 cUL = texelFetch(img, ivec2(floorCoord.x, floorCoord.y), 0);
  int indexUL = int(round((
    (int(channelNum == 0) * cUL.r) + (int(channelNum == 1) * cUL.g) + 
    (int(channelNum == 2) * cUL.b) + (int(channelNum == 3) * cUL.a)
  ) * 255.0));
  vec4 colorUL = vec4(reds[indexUL] / 255.0, greens[indexUL] / 255.0, blues[indexUL] / 255.0, 1.0);

  vec4 cUR = texelFetch(img, ivec2(ceilCoord.x, floorCoord.y), 0);
  int indexUR = int(round((
    (int(channelNum == 0) * cUR.r) + (int(channelNum == 1) * cUR.g) + 
    (int(channelNum == 2) * cUR.b) + (int(channelNum == 3) * cUR.a)
  ) * 255.0));
  vec4 colorUR = vec4(reds[indexUR] / 255.0, greens[indexUR] / 255.0, blues[indexUR] / 255.0, 1.0);

  vec4 cLL = texelFetch(img, ivec2(floorCoord.x, ceilCoord.y), 0);
  int indexLL = int(round((
    (int(channelNum == 0) * cLL.r) + (int(channelNum == 1) * cLL.g) + 
    (int(channelNum == 2) * cLL.b) + (int(channelNum == 3) * cLL.a)
  ) * 255.0));
  vec4 colorLL = vec4(reds[indexLL] / 255.0, greens[indexLL] / 255.0, blues[indexLL] / 255.0, 1.0);

  vec4 cLR = texelFetch(img, ivec2(ceilCoord.x, ceilCoord.y), 0);
  int indexLR = int(round((
    (int(channelNum == 0) * cLR.r) + (int(channelNum == 1) * cLR.g) + 
    (int(channelNum == 2) * cLR.b) + (int(channelNum == 3) * cLR.a)
  ) * 255.0));
  vec4 colorLR = vec4(reds[indexLR] / 255.0, greens[indexLR] / 255.0, blues[indexLR] / 255.0, 1.0);

  // https://www.reedbeta.com/blog/texture-gathers-and-coordinate-precision/
  vec2 weight = fract(vertTexCoord.xy * vec2(texSize - 1));

  vec4 colorU = mix(colorUL, colorUR, weight.x);
  vec4 colorL = mix(colorLL, colorLR, weight.x);
  vec4 color = mix(colorU, colorL, weight.y);

  gl_FragColor = vec4(color.rgb, fadeAlpha);
}

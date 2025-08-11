import java.io.File;
import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import processing.core.PApplet;
import processing.core.PGraphics;
import processing.core.PImage;
import processing.data.JSONArray;
import processing.data.JSONObject;
import processing.opengl.PShader;

public class IndexedPlayer {
  protected boolean isReady;

  protected List<PImage> images;
  protected List<ColorLUT> colorLUTs;
  protected int sequenceSize;

  protected PApplet sketch;
  protected File imageDir;
  protected float frameRate;

  protected PShader shader;
  protected int index;
  protected PImage shaderSetImage;

  public IndexedPlayer(PApplet sketch, File imgDir, float frameRate) {
    this.sketch = sketch;
    this.imageDir = imgDir;
    this.frameRate = frameRate;

    isReady = false;

    initialize();
  }

  public void initialize() {
    Thread t = new Thread() {
      public void run() {
        if (!imageDir.exists()) {
          println("Directory for image sequence " + imageDir.toString() + " not found");
          return;
        }

        File[] files = imageDir.listFiles();

        Arrays.sort(files);

        images = new ArrayList<PImage>();
        for (File f : files) {
          if (f.isFile()) {
            String name = f.getName().toLowerCase();
            if (name.endsWith(".png")) {
              images.add(sketch.loadImage(f.getAbsolutePath()));
            }
          }
        }

        try {
          colorLUTs = new ArrayList<ColorLUT>();
          JSONArray colorLUTdata = PApplet.loadJSONArray(new File(imageDir, "color_lut.json"));
          for (int i = 0; i < colorLUTdata.size(); i++) {
            JSONObject colorLUTdatum = colorLUTdata.getJSONObject(i);
            ColorLUT lut = new ColorLUT();
            lut.r = colorLUTdatum.getJSONArray("r").toFloatArray();
            lut.g = colorLUTdatum.getJSONArray("g").toFloatArray();
            lut.b = colorLUTdatum.getJSONArray("b").toFloatArray();
            colorLUTs.add(lut);
          }
          sequenceSize = colorLUTs.size();
        } catch (Exception e) {
          println("Unable to load color lookup table for IndexedPlayer " + imageDir.toString() + " Exception: " + e);
          return;
        }

        isReady = true;
      }
    };
    t.start();
  }

  public PShader initializeShader() {
    PShader shader = loadShader("decodeIndexedImageFrag.glsl", "texVert.glsl");

    shader.set("img", images.get(0));
    shader.set("channelNum", 0);
    shader.set("reds", colorLUTs.get(0).r);
    shader.set("greens", colorLUTs.get(0).g);
    shader.set("blues", colorLUTs.get(0).b);
    shader.set("fadeAlpha", 1f);

    return shader;
  }

  public boolean isReady() {
    return isReady;
  }

  public void update(float t) {
    if (!isReady) {
      return;
    }

    // find current image index
    index = (int) Math.floor((t % (sequenceSize / frameRate)) * frameRate);
    // just to be safe...
    index = Math.min(index, sequenceSize - 1);
  }

  public void draw() {
    if (!isReady) {
      return;
    }

    PGraphics g = sketch.g;

    g.push();
    g.rectMode(PGraphics.CENTER);

    if (shader == null) {
      shader = initializeShader();
    }

    g.shader(shader);
    g.noStroke();

    // find the image and color channel that contains the
    // data for the desired image
    int channelNum = (int) (index % 4);
    PImage img = images.get((int) (index / 4));
    ColorLUT colorLUT = colorLUTs.get(index);

    // set image and channel number
    if (img != shaderSetImage) {
      shader.set("img", img);
      shaderSetImage = img;
    }
    shader.set("channelNum", (int) channelNum);

    // set the color palette
    shader.set("reds", colorLUT.r);
    shader.set("greens", colorLUT.g);
    shader.set("blues", colorLUT.b);
    // if you want to fade out the image
    shader.set("fadeAlpha", 1.0f);
    
    // draw rectangle with shader applied
    g.rect(0, 0, img.width, img.height);
    g.resetShader();

    g.pop();
  }

}

import java.io.File;
import java.io.FileNotFoundException;
import java.net.URL;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import processing.core.PApplet;
import processing.core.PGraphics;
import processing.core.PImage;
import processing.opengl.PShader;

public class GrayscalePlayer {
  protected boolean isReady;

  protected List<PImage> images;
  protected int sequenceSize;

  protected PApplet sketch;
  protected File imageDir;
  protected float frameRate;

  protected PShader shader;
  protected int index;
  protected PImage shaderSetImage;

  public GrayscalePlayer(PApplet sketch, File imgDir, float frameRate) {
    this.sketch = sketch;
    this.imageDir = imgDir;
    this.frameRate = frameRate;

    isReady = false;

    initialize();
  }

  public void initialize() {
    // load compressed image data
    // do this in a thread to avoid blocking caller

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
          sequenceSize = Integer.parseInt(new String(Files.readAllBytes((new File(imageDir, "data.txt")).toPath())));
        } catch (FileNotFoundException e) {
          println("Unable to load color lookup table for IndexedPlayer " + imageDir.toString() + " Exception: " + e);
          return;
        } catch (Exception e) {
          println("Unable to read data file for grayscale image sequence " + imageDir.toString() + " Exception: " + e);
          return;
        }

        isReady = true;
      }
    };
    t.start();
  }

  public PShader initializeShader() {
    PShader shader = loadShader("decodeGrayscaleImageFrag.glsl", "texVert.glsl");

    shader.set("img", images.get(0));
    shader.set("channelNum", 0);
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

    // set image and channel number
    if (img != shaderSetImage) {
      shader.set("img", img);
      shaderSetImage = img;
    }
    shader.set("channelNum", (int) channelNum);

    // if you want to fade out the image
    shader.set("fadeAlpha", 1.0f);

    // draw rectangle with shader applied
    g.rect(0, 0, img.width, img.height);
    g.resetShader();

    g.pop();
  }

}

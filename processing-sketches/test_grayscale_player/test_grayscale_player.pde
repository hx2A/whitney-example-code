GrayscalePlayer grayscalePlayer;

void setup() {
  size(600, 600, P3D);
  ortho();
  
  frameRate(30);
  
  // create grayscale image player to manage compressed image assets
  grayscalePlayer = new GrayscalePlayer(this, dataFile("grayscale-image-data"), 5);
}

void draw() {
  background(0);
 
  translate(width / 2, height / 2);

  // update index player to advance image sequence
  grayscalePlayer.update(frameCount / 30.0);

  // draw index player image to Sketch window
  grayscalePlayer.draw();
}

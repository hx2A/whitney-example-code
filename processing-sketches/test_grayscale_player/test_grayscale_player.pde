GrayscalePlayer grayscalePlayer;

void setup() {
  size(600, 600, P3D);
  ortho();
  
  frameRate(30);
  
  grayscalePlayer = new GrayscalePlayer(this, dataFile("grayscale-image-data"), 5);
}

void draw() {
 background(0);
 
 translate(width / 2, height / 2);
 grayscalePlayer.update(frameCount / 30.0);
 grayscalePlayer.draw();
}

IndexedPlayer indexedPlayer;

void setup() {
  size(600, 600, P3D);
  ortho();
  
  frameRate(30);
  
  // create indexed image player to manage compressed image assets
  indexedPlayer = new IndexedPlayer(this, dataFile("indexed-image-data"), 5);
}

void draw() {
  background(0);
 
  translate(width / 2, height / 2);
 
  // update index player to advance image sequence
  indexedPlayer.update(frameCount / 30.0);
 
  // draw index player image to Sketch window
  indexedPlayer.draw();
}

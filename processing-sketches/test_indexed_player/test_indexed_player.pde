IndexedPlayer indexedPlayer;

void setup() {
  size(600, 600, P3D);
  ortho();
  
  frameRate(30);
  
  indexedPlayer = new IndexedPlayer(this, dataFile("indexed-image-data"), 5);
}

void draw() {
 background(0);
 
 translate(width / 2, height / 2);
 indexedPlayer.update(frameCount / 30.0);
 indexedPlayer.draw();
}

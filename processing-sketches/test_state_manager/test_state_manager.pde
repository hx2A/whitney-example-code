// The StateManager is a singleton class, so everyone
// uses the same instance.
StateManager stateManager = StateManager.getInstance();


void eval(String expr) {
  println(expr + ":", stateManager.evaluateStateExpr(expr));
}

void setup() {
  // Define a set of known states and set to true or false
  // All unknown/undefined states always evaluate to false
  // State names cannot contain spaces. Only use alphanumeric
  // characters and underscores.
  stateManager.setState("hot", true);
  stateManager.setState("cold", false);
  stateManager.setState("raining", false);
  stateManager.setState("snowing", false);

  // Test basic boolean expressions that use AND, OR, XOR, NOT and parentheses.
  // Boolean operators are case insensitive but I'm using the upper case here
  // for readability.

  println("Test Basic Boolean Expressions");
  eval("hot AND raining");
  eval("hot OR cold");
  eval("hot AND (raining OR snowing)");
  eval("NOT hot AND (raining OR snowing)");
  eval("hot XOR raining");

  // State "sleet" is undefined and is therefore false 
  eval("cold OR sleet");

  // Builtin Time states
  
  // first, set the time zone and location
  stateManager.setLocationInfo("US/Eastern", 40.75, -73.98);

  println("\nTest Daytime/Nighttime States");
  // true if daytime or nighttime for given location
  eval("daytime");
  eval("nighttime");

  println("\nTest Months");
  // true if current date is given month 
  eval("january");
  eval("february");
  eval("march");
  eval("april");
  eval("may");
  eval("june");
  eval("july");
  eval("august");
  eval("september");
  eval("october");
  eval("november");
  eval("december");

  // can use these with boolean expressions
  eval("august AND nighttime");

  println("\nTest Specific dates");
  // true for specific days
  eval("august10");
  eval("august11");
  eval("august12");

  println("\nTest Days of Week");
  // true for particular day of week
  eval("monday");
  eval("tuesday");
  eval("wednesday");
  eval("thursday");
  eval("friday");
  eval("saturday or sunday");

  println("\nTest Seasons");
  // true if current time is in season
  eval("summer");
  eval("fall");
  eval("winter");
  eval("spring");

  println("\nTest Season Boundaries");
  // true only on these specific days
  eval("summer_solstice");
  eval("winter_solstice");
  eval("vernal_equinox");
  eval("autumnal_equinox");

  println("\nTest Hours of the Day");
  // true only for specific hours of day (uses 24 hour clock)
  
  // true only from 10:00:00 PM to 10:59:59 PM
  eval("hour22");
  // true only from 3:00:00 AM to 3:59:59 AM
  eval("hour03");

  // time ranges
  // true only from 1:00:00 PM to 10:59:59 PM
  eval("hour13_22");
  // time ranges can span midnight
  // true only from 10:00:00 PM to 3:59:59 AM
  eval("hour22_03");

  println("\nTest Compound Time Expressions");
  // combine builtins with boolean operations
  eval("summer AND nighttime");
  eval("fall AND nighttime");
  eval("summer AND friday");
  eval("nighttime AND (august or september)");  
}

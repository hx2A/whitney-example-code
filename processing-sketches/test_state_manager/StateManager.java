import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.TimeZone;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class StateManager {
  protected static final Pattern HOUR_REGEX = Pattern.compile("^hour(\\d+)$");
  protected static final Pattern HOUR_RANGE_REGEX = Pattern.compile("^hour(\\d+)_(\\d+)$");
  protected static final String[] SEASONS = { "spring", "summer", "fall", "winter" };

  private static StateManager instance;

  protected Map<String, Boolean> states;

  protected Calendar time;
  protected double locationLat;
  protected double locationLon;
  protected int nowHour;
  protected String nowMonth;
  protected int nowDOM;
  protected String nowDOW;
  protected double dayFractionSunrise;
  protected double dayFractionSunset;
  protected double dayFractionNow;
  protected boolean nowNighttime;
  protected double currentSunDeclination;
  protected String nowSeason;
  protected String nowEarthPosition;
  protected long nowLastUpdated;

  private StateManager() {
    states = new HashMap<String, Boolean>();

    time = Calendar.getInstance();
    time.setTimeZone(TimeZone.getTimeZone("US/Eastern"));
    locationLat = 40.7528788;
    locationLon = -73.9765096;
    updateTimeAndFields();
  }

  public static StateManager getInstance() {
    if (instance == null) {
      instance = new StateManager();
    }

    return instance;
  }

  public Set<String> getKnownStates() {
    return states.keySet();
  }

  // ***** CONSTRUCTION / SETUP ***********************************************

  public void initiateState(String state) {
    state = state.toLowerCase();
    if (!states.containsKey(state)) {
      states.put(state, false);
    }
  }

  public void setLocationInfo(String timezone, double lat, double lon) {
    time.setTimeZone(TimeZone.getTimeZone(timezone));
    locationLat = lat;
    locationLon = lon;
  }

  // ***** DEPLOYMENT *********************************************************

  public boolean getState(String state) {
    if (System.currentTimeMillis() > nowLastUpdated + 1000) {
      updateTimeAndFields();
    }

    state = state.toLowerCase();
    if (states.containsKey(state)) {
      return states.get(state);
    }

    if (state.equals("true")) {
      return true;
    } else if (state.equals("false")) {
      return false;
    }

    if ((nowNighttime && state.equals("nighttime")) || !nowNighttime && state.equals("daytime")) {
      return true;
    }

    if (state.equals(nowMonth)) {
      return true;
    }

    if (state.startsWith(nowMonth) && Integer.parseInt(state.substring(nowMonth.length())) == nowDOM) {
      return true;
    }

    if (state.equals(nowDOW)) {
      return true;
    }

    if (state.equals(nowSeason)) {
      return true;
    }

    if (nowEarthPosition != null && state.equals(nowEarthPosition)) {
      return true;
    }

    Matcher m;
    m = HOUR_REGEX.matcher(state);
    if (m.find()) {
      return Integer.parseInt(m.group(1)) == nowHour;
    }
    m = HOUR_RANGE_REGEX.matcher(state);
    if (m.find()) {
      int startHour = Integer.parseInt(m.group(1));
      int endHour = Integer.parseInt(m.group(2));
      if (startHour < endHour) {
        return startHour <= nowHour && nowHour <= endHour;
      } else {
        return startHour <= nowHour || nowHour <= endHour;
      }
    }

    return false;
  }

  protected String convertStateExpr(String stateExpr) {
    StringBuilder expr = new StringBuilder();
    for (String token : stateExpr.split("\\b")) {
      switch (token.toUpperCase()) {
        case "AND":
          expr.append("&");
          break;
        case "OR":
          expr.append("|");
          break;
        case "XOR":
          expr.append("^");
          break;
        case "NOT":
          expr.append("!");
          break;
        default:
          expr.append(token);
      }
    }
    return expr.toString();
  }

  public boolean evaluateStateExpr(String stateExprInput) {
    return new Object() {
      int index = -1;
      int c = 0;
      String stateExpr;

      void nextChar() {
        c = (++index < stateExpr.length()) ? stateExpr.charAt(index) : -1;
      }

      void consumeWhitespace() {
        while (c == ' ')
          nextChar();
      }

      boolean isVarChar() {
        return ((c >= '0' && c <= '9') || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_');
      }

      boolean consume(int charToConsume) {
        consumeWhitespace();
        if (c == charToConsume) {
          nextChar();
          consumeWhitespace();
          return true;
        }
        return false;
      }

      public boolean parse() {
        stateExpr = convertStateExpr(stateExprInput);
        nextChar();
        boolean out = parseExpression();
        if (index < stateExpr.length())
          throw new RuntimeException(
              "Extra characters " + stateExpr.substring(index) + " in state expression " + stateExpr);
        return out;
      }

      boolean parseExpression() {
        boolean out = parseTerm();
        for (;;) {
          if (consume('&'))
            out &= parseTerm();
          else if (consume('|'))
            out |= parseTerm();
          else if (consume('^'))
            out ^= parseTerm();
          else
            return out;
        }
      }

      boolean parseTerm() {
        if (consume('!')) {
          return !parseTerm();
        }

        boolean out;
        int startIndex = index;

        if (consume('(')) {
          out = parseExpression();
          consume(')');
        } else if (isVarChar()) {
          while (isVarChar())
            nextChar();
          String substr = stateExpr.substring(startIndex, index);
          out = getState(substr);
        } else {
          throw new RuntimeException("Unexpected character " + (char) c + " found in state expression " + stateExpr);
        }

        return out;
      }
    }.parse();
  }

  // ***** RUNNING ************************************************************

  public void setState(String state, boolean value) {
    states.put(state.toLowerCase(), value);
  }

  public void setTimeWarpSpeed(float speed) {
    updateTime();
    updateTimeAndFields();
  }

  protected void updateTime() {
    time.setTimeInMillis(System.currentTimeMillis());
  }

  protected void updateTimeAndFields() {
    updateTime();

    nowHour = time.get(Calendar.HOUR_OF_DAY);
    nowMonth = time.getDisplayName(Calendar.MONTH, 2, Locale.ENGLISH).toLowerCase();
    nowDOM = time.get(Calendar.DAY_OF_MONTH);
    nowDOW = time.getDisplayName(Calendar.DAY_OF_WEEK, 2, Locale.ENGLISH).toLowerCase();

    double tz = (time.get(Calendar.ZONE_OFFSET) + time.get(Calendar.DST_OFFSET)) / (60 * 60 * 1000d);
    double julianDate = time.getTimeInMillis() / 86400000d + 2440587.5;
    double julianCentury = (julianDate - 2451545) / 36525d;
    double geomMeanLongSun = (280.46646 + julianCentury * (36000.76983 + julianCentury * 0.0003032)) % 360;
    double geomMeanAnomSun = 357.52911 + julianCentury * (35999.05029 - 0.0001537 * julianCentury);
    double eccentEarthOrbit = 0.016708634 - julianCentury * (0.000042037 + 0.0000001267 * julianCentury);
    double sunEqOfCenter = sin(geomMeanAnomSun)
        * (1.914602 - julianCentury * (0.004817 + 0.000014 * julianCentury))
        + sin(2 * geomMeanAnomSun) * (0.019993 - 0.000101 * julianCentury)
        + sin(3 * geomMeanAnomSun) * 0.000289;
    double sunTrueLong = geomMeanLongSun + sunEqOfCenter;
    double sunAppLong = sunTrueLong - 0.00569 - 0.00478 * sin(125.04 - 1934.136 * julianCentury);
    double meanObliqEcliptic = 23
        + (26 + ((21.448 - julianCentury * (46.815 + julianCentury * (0.00059 - julianCentury * 0.001813)))) / 60d)
            / 60d;
    double obliqCorr = meanObliqEcliptic + 0.00256 * cos(125.04 - 1934.136 * julianCentury);
    currentSunDeclination = (arcsin(sin(obliqCorr) * sin(sunAppLong)));
    double varY = tan(obliqCorr / 2d) * tan(obliqCorr / 2d);
    double eqOfTime = 4
        * degrees(varY * sin(2 * geomMeanLongSun) - 2 * eccentEarthOrbit * sin(geomMeanAnomSun)
            + 4 * eccentEarthOrbit * varY * sin(geomMeanAnomSun) * cos(2 * geomMeanLongSun)
            - 0.5 * varY * varY * sin(4 * geomMeanLongSun)
            - 1.25 * eccentEarthOrbit * eccentEarthOrbit * sin(2 * geomMeanAnomSun));
    double haSunrise = arccos(
        cos(90.833) / (cos(locationLat) * cos(currentSunDeclination)) - tan(locationLat) * tan(currentSunDeclination));
    double solarNoon = (720 - 4 * locationLon - eqOfTime + tz * 60) / 1440d;
    dayFractionSunrise = solarNoon - haSunrise * 4 / 1440d;
    dayFractionSunset = solarNoon + haSunrise * 4 / 1440d;
    dayFractionNow = (time.get(Calendar.SECOND) + time.get(Calendar.MINUTE) * 60 + nowHour * 3600) / 86400d;

    nowSeason = SEASONS[(int) (sunAppLong / 90 % 4)];
    nowNighttime = dayFractionNow < dayFractionSunrise || dayFractionNow > dayFractionSunset;
    if (withinTargetRange(sunAppLong, 90, 0.041)) {
      nowEarthPosition = "summer_solstice";
    } else if (withinTargetRange(sunAppLong, 270, 0.041)) {
      nowEarthPosition = "winter_solstice";
    } else if (withinTargetRange(sunAppLong, 360, 0.041) || withinTargetRange(sunAppLong, 0, 0.041)) {
      nowEarthPosition = "vernal_equinox";
    } else if (withinTargetRange(sunAppLong, 180, 0.041)) {
      nowEarthPosition = "autumnal_equinox";
    } else {
      nowEarthPosition = null;
    }

    // logger.log(Level.INFO, "Set date & time to " + getDateTimeStr());

    nowLastUpdated = System.currentTimeMillis();
  }

  public String getDateTimeStr() {
    SimpleDateFormat formatter = new SimpleDateFormat("EEEE, MMMM dd, yyyy hh:mm a");
    return formatter.format(time.getTime());
  }

  public long getTimeInMillis() {
    updateTime();
    return time.getTimeInMillis();
  }

  public Calendar getCalendar() {
    updateTime();
    return time;
  }

  public double getDayFractionNow() {
    return dayFractionNow;
  }

  public double getDayFractionSunrise() {
    return dayFractionSunrise;
  }

  public double getDayFractionSunset() {
    return dayFractionSunset;
  }

  public double getCurrentSunDeclination() {
    return currentSunDeclination;
  }

  // ***** MISC ***************************************************************

  protected boolean withinTargetRange(double x, double target, double range) {
    return x > target - range && x < target + range;
  }

  protected double degrees(double x) {
    return x * 180 / Math.PI;
  }

  protected double sin(double x) {
    return Math.sin(x * Math.PI / 180d);
  }

  protected double cos(double x) {
    return Math.cos(x * Math.PI / 180d);
  }

  protected double tan(double x) {
    return Math.tan(x * Math.PI / 180d);
  }

  protected double arcsin(double theta) {
    return Math.asin(theta) * 180d / Math.PI;
  }

  protected double arccos(double theta) {
    return Math.acos(theta) * 180d / Math.PI;
  }

}

#-------------------------------------------------
#   Imports
#-------------------------------------------------
import re
from enum import StrEnum
from ToolBox_ECS_V1.ToolBox_Logger import OutputLogger

#-------------------------------------------------
#   Enums
#-------------------------------------------------

log:OutputLogger = OutputLogger().get_instance()

#-------------------------------------------------
#   Enums
#-------------------------------------------------


class ToolBox_Timezone_Patterns (StrEnum):
    """
    Exhaustive mapping for US states + DC and Canadian provinces/territories.
    Keys use the pattern <TZ>_<XX> where <TZ> is a 3-letter TZ abbrev and <XX>
    is the US state postal code or the CA province/territory code (or DC).
    Values are representative IANA region strings "{Country}/{Region}".
    """
    # --------------------
    # ADDITIONAL COMMON NORTH AMERICA TIMEZONES (general)
    # --------------------
    EST = "America/New_York"
    EDT = "America/New_York"
    CST = "America/Chicago"
    CDT = "America/Chicago"
    MST = "America/Denver"
    MDT = "America/Denver"
    PST = "America/Los_Angeles"
    PDT = "America/Los_Angeles"
    AKST = "America/Anchorage"
    AKDT = "America/Anchorage"
    HST = "Pacific/Honolulu"
    AST = "America/Halifax"
    ADT = "America/Halifax"
    NST = "America/St_Johns"
    NDT = "America/St_Johns"

    # --------------------
    # UNITED STATES (50 + DC)
    # --------------------
    # Alabama
    CST_AL = "America/Chicago"
    CDT_AL = "America/Chicago"

    # Alaska
    AKST_AK = "America/Anchorage"
    AKDT_AK = "America/Anchorage"

    # Arizona (most of AZ does not observe DST)
    MST_AZ = "America/Phoenix"

    # Arkansas
    CST_AR = "America/Chicago"
    CDT_AR = "America/Chicago"

    # California
    PST_CA = "America/Los_Angeles"
    PDT_CA = "America/Los_Angeles"

    # Colorado
    MST_CO = "America/Denver"
    MDT_CO = "America/Denver"

    # Connecticut
    EST_CT = "America/New_York"
    EDT_CT = "America/New_York"

    # Delaware
    EST_DE = "America/New_York"
    EDT_DE = "America/New_York"

    # District of Columbia
    EST_DC = "America/New_York"
    EDT_DC = "America/New_York"

    # Florida (eastern and western panhandle)
    EST_FL = "America/New_York"      # most of FL
    EDT_FL = "America/New_York"
    CST_FL = "America/Chicago"       # western panhandle
    CDT_FL = "America/Chicago"

    # Georgia
    EST_GA = "America/New_York"
    EDT_GA = "America/New_York"

    # Hawaii
    HST_HI = "Pacific/Honolulu"

    # Idaho (south & most = Mountain, panhandle = Pacific)
    MST_ID = "America/Boise"
    MDT_ID = "America/Boise"
    PST_ID = "America/Los_Angeles"   # Idaho panhandle (north)
    PDT_ID = "America/Los_Angeles"

    # Illinois
    CST_IL = "America/Chicago"
    CDT_IL = "America/Chicago"

    # Indiana (mostly Eastern; some counties historical exceptions)
    EST_IN = "America/Indiana/Indianapolis"
    EDT_IN = "America/Indiana/Indianapolis"
    CST_IN = "America/Chicago"       # some NW/SE counties (legacy)
    CDT_IN = "America/Chicago"

    # Iowa
    CST_IA = "America/Chicago"
    CDT_IA = "America/Chicago"

    # Kansas (most Central, some west Mountain)
    CST_KS = "America/Chicago"
    CDT_KS = "America/Chicago"
    MST_KS = "America/Denver"        # western KS
    MDT_KS = "America/Denver"

    # Kentucky (east = Eastern, west = Central)
    EST_KY = "America/New_York"
    EDT_KY = "America/New_York"
    CST_KY = "America/Chicago"
    CDT_KY = "America/Chicago"

    # Louisiana
    CST_LA = "America/Chicago"
    CDT_LA = "America/Chicago"

    # Maine
    EST_ME = "America/New_York"
    EDT_ME = "America/New_York"

    # Maryland
    EST_MD = "America/New_York"
    EDT_MD = "America/New_York"

    # Massachusetts
    EST_MA = "America/New_York"
    EDT_MA = "America/New_York"

    # Michigan (mostly Eastern; parts of Upper Peninsula = Central)
    EST_MI = "America/Detroit"
    EDT_MI = "America/Detroit"
    CST_MI = "America/Chicago"       # some Upper Peninsula counties
    CDT_MI = "America/Chicago"

    # Minnesota
    CST_MN = "America/Chicago"
    CDT_MN = "America/Chicago"

    # Mississippi
    CST_MS = "America/Chicago"
    CDT_MS = "America/Chicago"

    # Missouri
    CST_MO = "America/Chicago"
    CDT_MO = "America/Chicago"

    # Montana
    MST_MT = "America/Denver"
    MDT_MT = "America/Denver"

    # Nebraska (central & mountain parts)
    CST_NE = "America/Chicago"
    CDT_NE = "America/Chicago"
    MST_NE = "America/Denver"        # western Nebraska
    MDT_NE = "America/Denver"

    # Nevada (mostly Pacific; some mountain border exceptions)
    PST_NV = "America/Los_Angeles"
    PDT_NV = "America/Los_Angeles"
    MST_NV = "America/Denver"        # e.g., West Wendover historically
    MDT_NV = "America/Denver"

    # New Hampshire
    EST_NH = "America/New_York"
    EDT_NH = "America/New_York"

    # New Jersey
    EST_NJ = "America/New_York"
    EDT_NJ = "America/New_York"

    # New Mexico
    MST_NM = "America/Denver"
    MDT_NM = "America/Denver"

    # New York
    EST_NY = "America/New_York"
    EDT_NY = "America/New_York"

    # North Carolina
    EST_NC = "America/New_York"
    EDT_NC = "America/New_York"

    # North Dakota (central & mountain)
    CST_ND = "America/Chicago"
    CDT_ND = "America/Chicago"
    MST_ND = "America/Denver"
    MDT_ND = "America/Denver"

    # Ohio
    EST_OH = "America/New_York"
    EDT_OH = "America/New_York"

    # Oklahoma
    CST_OK = "America/Chicago"
    CDT_OK = "America/Chicago"

    # Oregon (mostly Pacific; some east uses Mountain)
    PST_OR = "America/Los_Angeles"
    PDT_OR = "America/Los_Angeles"
    MST_OR = "America/Boise"         # eastern OR uses America/Boise
    MDT_OR = "America/Boise"

    # Pennsylvania
    EST_PA = "America/New_York"
    EDT_PA = "America/New_York"

    # Rhode Island
    EST_RI = "America/New_York"
    EDT_RI = "America/New_York"

    # South Carolina
    EST_SC = "America/New_York"
    EDT_SC = "America/New_York"

    # South Dakota (east = Central, west = Mountain)
    CST_SD = "America/Chicago"
    CDT_SD = "America/Chicago"
    MST_SD = "America/Denver"
    MDT_SD = "America/Denver"

    # Tennessee (east = Eastern, middle/west = Central)
    EST_TN = "America/New_York"      # East Tennessee
    EDT_TN = "America/New_York"
    CST_TN = "America/Chicago"       # Middle/West Tennessee
    CDT_TN = "America/Chicago"

    # Texas (mostly Central; far west = Mountain)
    CST_TX = "America/Chicago"
    CDT_TX = "America/Chicago"
    MST_TX = "America/El_Paso"       # far west TX (El Paso)
    MDT_TX = "America/El_Paso"

    # Utah
    MST_UT = "America/Denver"
    MDT_UT = "America/Denver"

    # Vermont
    EST_VT = "America/New_York"
    EDT_VT = "America/New_York"

    # Virginia
    EST_VA = "America/New_York"
    EDT_VA = "America/New_York"

    # Washington
    PST_WA = "America/Los_Angeles"
    PDT_WA = "America/Los_Angeles"

    # West Virginia
    EST_WV = "America/New_York"
    EDT_WV = "America/New_York"

    # Wisconsin
    CST_WI = "America/Chicago"
    CDT_WI = "America/Chicago"

    # Wyoming
    MST_WY = "America/Denver"
    MDT_WY = "America/Denver"

    # --------------------
    # CANADA (provinces + territories)
    # --------------------
    # Alberta
    MST_AB = "America/Edmonton"
    MDT_AB = "America/Edmonton"

    # British Columbia (mostly Vancouver; some east/north exceptions)
    PST_BC = "America/Vancouver"
    PDT_BC = "America/Vancouver"
    MST_BC = "America/Edmonton"      # some east BC regions use Mountain

    # Manitoba
    CST_MB = "America/Winnipeg"
    CDT_MB = "America/Winnipeg"

    # New Brunswick
    AST_NB = "America/Moncton"
    ADT_NB = "America/Moncton"

    # Newfoundland & Labrador
    NST_NL = "America/St_Johns"
    NDT_NL = "America/St_Johns"

    # Northwest Territories
    MST_NT = "America/Yellowknife"
    MDT_NT = "America/Yellowknife"

    # Nova Scotia
    AST_NS = "America/Halifax"
    ADT_NS = "America/Halifax"

    # Nunavut (multiple zones; representative choices)
    EST_NU = "America/Iqaluit"       # some parts observe Eastern
    EDT_NU = "America/Iqaluit"
    CST_NU = "America/Rankin_Inlet"  # central Nunavut areas
    CDT_NU = "America/Rankin_Inlet"
    MST_NU = "America/Yellowknife"   # western Nunavut areas (representative)
    MDT_NU = "America/Yellowknife"

    # Ontario (mostly Eastern; some northwest is Central)
    EST_ON = "America/Toronto"
    EDT_ON = "America/Toronto"
    CST_ON = "America/Winnipeg"      # some far NW communities

    # Prince Edward Island
    AST_PE = "America/Halifax"
    ADT_PE = "America/Halifax"

    # Quebec (most uses Eastern; far east uses Atlantic)
    EST_QC = "America/Toronto"       # southern QC (Montreal/Toronto canonical)
    EDT_QC = "America/Toronto"
    AST_QC = "America/Halifax"       # eastern Quebec regions

    # Saskatchewan (mostly no DST)
    CST_SK = "America/Regina"        # Saskatchewan generally stays on CST year-round

    # Yukon
    MST_YT = "America/Whitehorse"    # Yukon uses America/Whitehorse (no DST historically)

    # --------------------
    # MEXICO (representative major zones included)
    # --------------------
    CST_MX = "America/Mexico_City"
    CDT_MX = "America/Mexico_City"
    MST_MX = "America/Chihuahua"
    MDT_MX = "America/Chihuahua"
    PST_MX = "America/Tijuana"
    PDT_MX = "America/Tijuana"
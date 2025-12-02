#-------------------------------------------------
#   Imports
#-------------------------------------------------
from enum import StrEnum
from ...ToolBox_Logger import OutputLogger

#-------------------------------------------------
#   Variables
#-------------------------------------------------

log:OutputLogger = OutputLogger().get_instance()

#-------------------------------------------------
#   Enums
#-------------------------------------------------

class ToolBox_Amount_Options (StrEnum):
    ANY = 'any'
    ALL = 'all'

class ToolBox_Entity_Types (StrEnum):
    NONE = 'not_assigned'
    OTHER = 'other'
    FILE = 'file'
    FILE_TXT = 'file_txt'
    FILE_CSV = 'file_csv'
    FILE_JIL = 'file_jil'
    FILE_JOB = 'file_job'
    FILE_JSON = 'file_json'
    FILE_YAML = 'file_yaml'
    FILE_XLSX = 'file_xlsx'
    DEPENDENCY = 'dependency'
    IWS_XLS_RUNBOOK = 'iws_xlsx_runbook'
    IWS_TXT_CALENDAR = 'iws_txt_calendar'
    IWS_TXT_RCG = 'iws_txt_rcg'
    IWS_JOB_STREAM = 'iws_job_stream'
    IWS_JOB = 'iws_job'
    IWS_TIMING = 'iws_timing'
    IWS_RUNCYCLE = 'iws_runcycle'
    IWS_RUNCYCLEGROUP = 'iws_runcyclegroup'
    IWS_FOLLOW = 'iws_follow'
    IWS_FOLLOW_JOIN = 'iws_follow_join'
    IWS_RESOURCE = 'iws_resource'
    IWS_OPENS = 'iws_opens'
    IWS_PROMPT = 'iws_prompt'
    IWS_CALENDAR = 'iws_calendar'


class ToolBox_REGEX_Patterns (StrEnum):
    # ----GENERAL LINE Items----
    BLANK_LINE = r'^\s*$'
    NOTE_LINE = r'^ ?(?:#+(?![^\s]+[^!:])) ?(?P<note>.*)'
    # ----GENERAL PART Items----
    YEAR_MONTH_DAY_PART = r'(?P<year>\d{2,4})[-\/\.]?(?P<month>\d{2})[-\/\.]?(?P<day>\d{2,4})'
    DAY_MONTH_YEAR_PART = r'(?P<day>\d{2,4})[-\/\.]?(?P<month>\d{2})[-\/\.]?(?P<year>\d{2,4})'
    MONTH_DAY_YEAR_PART = r'(?P<month>\d{1,2})[-\/\.]?(?P<day>\d{1,2})[-\/\.]?(?P<year>\d{2,4})'
    UNKNOWN_DATE_PART = r'(?P<date_v1>\d{2,4})[-\/\.]?(?P<date_v2>\d{2})[-\/\.]?(?P<date_v3>\d{2,4})'
    # ----GENERAL LIST Items----
    COMMA_SEP_NUMBER_LIST = r'(?<![\d\/-])\b(?P<numbers>[-+]?\d+(?:\.\d+)?)\b(?![\/-])'
    # ----IWS LINE Items----
    IWS_STREAM_START_LINE = r'^\s*[Ss][Cc][Hh][Ee][Dd][Uu][Ll][Ee]\s*(?P<workstation>[\/|@][^\s]+#)(?P<folder>[^\s]*(?:[^\s]*)*\/)*(?P<stream>[^\s.*?\.]*)'
    IWS_STREAM_EDGE_LINE = r'^\s*(?P<stream_edge>:){1}'
    IWS_STREAM_END_LINE = r'^\s*(?P<end>[Ee][Nn][Dd])\b'
    IWS_JOB_START_LINE = r'^\s*(?P<workstation>[\/@][^\s]+#)(?P<folder>\/[^\/\s]*(?:\/[^\/\s]*)*\/)*(?P<job>[^\s.*?\.]*).*?[^\s]?([^\s@]*)?(?: [Aa][Ss] )?(?P<alias>[^\s@]*)?'
    IWS_DESCRIPTION_LINE = r'^\s*[Dd][Ee][Ss][Cc][Rr][Ii][Pp][Tt][Ii][Oo][Nn]\s(?:[\"\']{1}?(?P<description>[^\s]+.*)[\"\']{1}?)'
    IWS_DRAFT_LINE = r'^\s*(?P<draft>[Dd][Rr][Aa][Ff][Tt])'
    IWS_PRIORITY_LINE = r'^\s*(?:[Pp][Rr][Ii][Oo][Rr][Ii][Tt][Yy] ?(?P<priority>[\d]+))'
    IWS_ONOVERLAP_LINE = r'^\s*(?:[Oo][Nn][Oo][Vv][Ee][Rr][Ll][Aa][Pp] *(?P<onoverlap>[^\s]+)\b)'
    IWS_MATCHING_LINE = r'^\s*[Mm][Aa][Tt][Ch][Hh][Ii][Nn][Gg]\s*(?:(?P<matching>[Ss][Aa][Mm][Ee][Dd][Aa][Yy]|[Pp][Rr][Ee][Vv][Ii][Oo][Uu][Ss]))'
    IWS_CALENDAR_DECORATOR_LINE = r'^ ?\$[Cc][Aa][Ll][Ee][Nn][Dd][Aa][Rr]'
    # ----IWS PART Items----
    IWS_OBJECT_PATH_PARTS = r'(?P<workstation>[\/|@][^\s]+#)(?P<folder>\/[^\s]+\/)(?P<object>[^\s]+)\.(?P<sub_object>@|[^\s]+)'
    IWS_RUNCYCLEGROUP_PART = r'[Rr][Uu][Nn][Cc][Yy][Cc][Ll][Ee][Gg][Rr][Oo][Uu][Pp] *(?P<rcg_folder>\/[^\s]+\/)(?P<rcg_name>[^\s]+)'
    IWS_RUNCYCLE_PART = r'(?:[Rr][Uu][Nn][Cc][Yy][Cc][Ll][Ee])\s+(?P<rc_name>[^\s]*)(?:\s*(?P<target_folder>\/[^\s]+\/)(?P<target_name>[^\s]+))?'
    IWS_PLUS_MINUS_DAYS_PART = r'(?P<plus_minus>[+-])(?P<days>\d)\s+[Dd][Aa][Yy][Ss]?'
    IWS_FREEDAYS_PART = r'[Ff][Rr][Ee][Ee][Dd][Aa][Yy][Ss]\s*(?P<calendar_folder>\/[^\s]+\/)(?P<calendar>[^\s]+)\s*(?P<saterday>\-?[Ss][Aa])?\s*(?P<sunday>\-?[Ss][Uu])?'
    IWS_TIMEZONE_PART = r'(?:[Tt][Zz]|[Tt][Ii][Mm][Ee][Zz][Oo][Nn][Ee])\s*(?P<timezone>[^\s]*)'
    IWS_FDIGNORE_PART = r'(?P<fdignore>\b[Ff][Dd][Ii][Gg][Nn][Oo][Rr][Ee]\b)'
    IWS_FDPREV_PART = r'(?P<fdprev>\b[Ff][Dd][Pp][Rr][Ee][Vv]\b)'
    IWS_FDNEXT_PART = r'(?P<fdnext>\b[Ff][Dd][Nn][Ee][Xx][Tt]\b)'
    IWS_END_PART = r'(?P<end>\b[Ee][Nn][Dd](?![Jj][Oo][Ii][Nn])\b)'
    IWS_ON_PART = r'(?P<on>\b[Oo][Nn]\b)'
    IWS_EXCEPT_PART = r'(?P<except>\b[Ee][Xx][Cc][Ee][Pp][Tt]\b)'
    IWS_SUBSET_PART = r'[Ss][Uu][Bb][Ss][Ee][Tt]\s*(?P<subset>[^\s]*)\s*(?P<and_or>[^\s]*)'
    IWS_BYMONTHDAY_PART = r'[Bb][Yy][Mm][Oo][Nn][Tt][Hh][Dd][Aa][Yy]\s*=(?:[\s\,]*(?P<monthday>[-+]?\d+))*'
    IWS_BYDAY_PART = r'[Bb][Yy][Dd][Aa][Yy]\s*=\s*(?:(?P<byday>\d*\s*(?:[Mm][Oo]|[Tt][Uu]|[Ww][Ee]|[Tt][Hh]|[Ff][Rr]|[Ss][Aa]|[Ss][Uu]))[ \,]*)*'
    IWS_INTERVAL_PART = r'[Ii][Nn][Tt][Ee][Rr][Vv][Aa][Ll]\s*\=\s*(?P<interval>\d+)'
    IWS_FREQUENCY_PART = r'[Ff][Rr][Ee][Qq]\s*\=\s*(?P<frequency>[\w]+)'
    IWS_VALIDTO_PART = r'(?<=[Vv][Aa][Ll][Ii][Dd][Tt][Oo]\s)(?P<date_v1>\d{1,4})[-\/\.]?(?P<date_v2>\d{1,2})[-\/\.]?(?P<date_v3>\d{1,4})'
    IWS_VALIDFROM_PART = r'(?<=[Vv][Aa][Ll][Ii][Dd][Ff][Rr][Oo][Mm]\s)(?P<date_v1>\d{1,4})[-\/\.]?(?P<date_v2>\d{1,2})[-\/\.]?(?P<date_v3>\d{1,4})'
    IWS_DESCRIPTION_PART = r'[Dd][Ee][Ss][Cc][Rr][Ii][Pp][Tt][Ii][Oo][Nn]\s(?:[\"\']{1}?(?P<description>[^\s]+.*)[\"\']{1}?)'
    # ----IWS LIST Items----
    IWS_COMMA_SEP_WEEKDAY_LIST = r'(?:(?P<byday>\b\d?(?:[Mm][Oo]|[Tt][Uu]|[Ww][Ee]|[Tt][Hh]|[Ff][Rr]|[Ss][Aa]|[Ss][Uu])\b)[ \,]*)'

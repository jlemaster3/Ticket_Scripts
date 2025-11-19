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
    IWS_JOB_STREAM = 'iws_job_stream'
    IWS_JOB = 'iws_job'
    IWS_TIMING = 'iws_timing'
    IWS_RUNCYCLE = 'iws_runcycle'
    IWS_FOLLOW = 'iws_follow'
    IWS_JOIN = 'iws_join'
    IWS_RESOURCE = 'iws_resource'
    IWS_OPENS = 'iws_opens'
    IWS_PROMPT = 'iws_prompt'
    IWS_CALENDAR = 'iws_calendar'


class ToolBox_REGEX_Patterns (StrEnum):
    BLANK_LINE = r'^\s*$'
    NOTE_LINE = r'^ ?(?:#+(?![^\s]+[^!:])) ?(?P<note>.*)'
    YEAR_MONTH_DAY = r'(?P<year>\d{2,4})[-\/\.]?(?P<month>\d{2})[-\/\.]?(?P<day>\d{2,4})'
    IWS_TIMEZONE = r'(?:\s+(?:[Tt][Zz]|[Tt][Ii][Mm][Ee][Zz][Oo][Nn][Ee])\s+(?P<time_zone>[^\s]*))'
    IWS_OBJECT_PATH_PARTS = r'(?P<workstation>[\/|@][^\s]+#)(?P<folder>\/[^\s]+\/)(?P<object>[^\s]+)\.(?P<sub_object>@|[^\s]+)'
    IWS_STREAM_START_LINE = r'^\s*[Ss][Cc][Hh][Ee][Dd][Uu][Ll][Ee]\s*(?P<workstation>[\/|@][^\s]+#)(?P<folder>[^\s]*(?:[^\s]*)*\/)*(?P<stream>[^\s.*?\.]*)'
    IWS_STREAM_EDGE_LINE = r'^\s*(?P<stream_edge>:){1}'
    IWS_STREAM_END_LINE = r'^\s*(?P<end>[Ee][Nn][Dd])\b'
    IWS_JOB_START_LINE = r'^\s*(?P<workstation>[\/@][^\s]+#)(?P<folder>\/[^\/\s]*(?:\/[^\/\s]*)*\/)*(?P<job>[^\s.*?\.]*).*?[^\s]?([^\s@]*)?(?: [Aa][Ss] )?(?P<alias>[^\s@]*)?'
    IWS_DESCRIPTION_LINE = r'^\s*[Dd][Ee][Ss][Cc][Rr][Ii][Pp][Tt][Ii][Oo][Nn]\s(?:[\"\']{1}?(?P<description>[^\s]+.*)[\"\']{1}?)'
    IWS_DRAFT_LINE = r'^\s*(?P<draft>[Dd][Rr][Aa][Ff][Tt])'
    IWS_PRIORITY_LINE = r'^\s*(?:[Pp][Rr][Ii][Oo][Rr][Ii][Tt][Yy] ?(?P<priority>[\d]+))'
    IWS_ONOVERLAP_LINE = r'^\s*(?:[Oo][Nn][Oo][Vv][Ee][Rr][Ll][Aa][Pp] *(?P<onoverlap>[^\s]+)\b)'
    IWS_MATCHING_LINE = r'^\s*[Mm][Aa][Tt][Ch][Hh][Ii][Nn][Gg]\s*(?:(?P<matching>[Ss][Aa][Mm][Ee][Dd][Aa][Yy]|[Pp][Rr][Ee][Vv][Ii][Oo][Uu][Ss]))'
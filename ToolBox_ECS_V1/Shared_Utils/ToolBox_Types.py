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
class ToolBox_Amount_Options (StrEnum):
    ANY = 'any'
    ALL = 'all'

class ToolBox_File_Types (StrEnum):
    CSV = '.csv'
    JIL = '.jil'
    JOB = '.job'
    YAML = '.yaml'

class ToolBox_Entity_Types (StrEnum):
    NONE = 'not_assigned'
    OTHER = 'other'
    FILE = 'file'
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
    
class ToolBox_REGEX_Patterns (StrEnum):
    """EDIT PATTERNS AT YOUR OWN RISK !!! """
    BLANK_LINE = r'^\s*$'
    NOTE_LINE = r'^ *#+(?![^\s]+:)\s*(.*)'
    YEAR_MONTH_DAY = r'(\d{4})(\d{2})(\d{2}),?'
    IWS_OBJECT_PATH_PARTS = r'([\/|@][^\s]+#)(\/[^\s]+\/)([^\s]+)\.(@|[^\s]+)'
    IWS_CARRYFORWARD = r'([Cc][Aa][Rr]{2}[Yy][Ff][Oo][Rr][Ww][Aa][Rr][Dd])'
    IWS_ENV_ISOLATE = r'^\s*#{1}(?!\!)([^\s]*):'
    IWS_ENV_EXCLUDE = r'^\s*#{1}\!{1}\s*([^\s]*):'
    IWS_FD_OFFSET_OPTION = r'[Ff][Dd][Nn][Ee][Xx][Tt]|[Ff][Dd][Pp][Rr][Ee][Vv]|[Ff][Dd][Ii][Gg][Nn][Oo][Rr]'
    IWS_STREAM_START_LINE = r'^\s*[Ss][Cc][Hh][Ee][Dd][Uu][Ll][Ee]\s*([\/|@][^\s]+#)([^\s]*(?:[^\s]*)*\/)*([^\s.*?\.]*)'
    IWS_STREAM_EDGE_LINE = r'^\s*(:){1}'
    IWS_STREAM_END_LINE = r'^\s*([Ee][Nn][Dd]){1}(?![Jj][Oo][Ii][Nn])'
    IWS_DRAFT_LINE = r'^\s*([Dd][Rr][Aa][Ff][Tt])'
    IWS_ON_REQUEST_LINE = r'^\s*([Oo][Nn]\s+[Rr][Ee][Qq][Uu][Ee][Ss][Tt])'
    IWS_JOB_START_LINE = r'^\s*([\/@][^\s]+#)(\/[^\/\s]*(?:\/[^\/\s]*)*\/)*([^\s.*?\.]*).*?[^\s]?([^\s@]*)?(?: [Aa][Ss] )?([^\s@]*)?'
    IWS_ON_RUNCYCLE_GROUP_LINE = r'(?:[Oo][Nn])\s+(?:[Rr][Uu][Nn][Cc][Yy][Cc][Ll][Ee])\s+([^\s]*)\s+(:?\$[Rr][Cc][Gg])\s+(\/[^\s]+\/)([^\s]+)\b'
    IWS_ON_RUNCYCLE_FREQ_LINE = r'(?:[Oo][Nn])\s+(?:[Rr][Uu][Nn][Cc][Yy][Cc][Ll][Ee])\s+([^\s]*)\s+"\s*[Ff][Rr][Ee][Qq]\s*=\s*([Dd][Aa][Ii][Ll][Yy]|[Ww][Ee]{2}[Kk][Ll][Yy]|[Mm][Oo][Nn][Tt][Hh][Ll][Yy]|[Yy][Ee][Aa][Rr][Ll][Yy])\s*;\s*INTERVAL=([\d]*)\s*;\s*([^\s]*)\s*=\s*([^\s]*)\s*"\s*(?:[Ss][Uu][Bb][Ss][Ee][Tt]\s*([^\s]+)\s+([Aa][Nn][Dd]|[Oo][Rr]))'
    IWS_ON_DAY_LINE = r'^\s*(?:[Oo][Nn])\s*(?:([Mm][Oo])|([Tt][Uu])|([Ww][Ee])|([Tt][Hh])|([Ff][Rr])|([Ss][Aa])|([Ss][Uu]))'
    IWS_ON_DATE_LINE = r'^\s*(?:[Oo][Nn])(?![Rr][Uu][Nn][Cc][Yy][Cc][Ll][Ee]) ?|,?(?:(\d{4})(\d{2})(\d{2}))'
    IWS_FOLLOWS_LINE = r'\s*[Ff][Oo][Ll][Ll][Oo][Ww][Ss]\s+(?:([\/|\@][^\s]*#)((?:\/[^\s]+)+\/)([^.\s]+)(?:\.([^\s@]+|@))?|([^\s]+))'
    IWS_AT_SCHEDTIME = r'\b([Aa][Tt]|[Ss][Cc][Hh][Ee][Dd][Tt][Ii][Mm][Ee])\s+([\d]{4})\b(?:\s+[Tt][Zz]\s+([^\s]*))?'
    IWS_PLUS_MINUS_DAYS = r'([\+|\-]\d+)\s+([Dd][Aa][Yy][Ss])'
    IWS_VALIDTO_VALIDFROM = r'([Vv][Aa][Ll][Ii][Dd][Tt][Oo]|[Vv][Aa][Ll][Ii][Dd][Ff][Rr][Oo][Mm])\s*(\d{4})(\d{2})(\d{2})'
    IWS_MATCHING_LINE = r'^\s*[Mm][Aa][Tt][Ch][Hh][Ii][Nn][Gg]\s([^\s]+)\b'
    IWS_PREVIOUS_SAMEDAY = r'([Ss][Aa][Mm][Ee][Dd][Aa][Yy]|[Pp][Rr][Ee][Vv][Ii][Oo][Uu][Ss])'
    IWS_JOIN_LINE = r'^\s*[Jj][Oo][Ii][Nn]\s+([^\s]*)\s*(\d|[Aa][Ll]+)\s*OF'
    IWS_ENDJOIN_LINE = r'^\s*([Ee][Nn][Dd][Jj][Oo][Ii][Nn])'
    IWS_DESCRIPTION_LINE = r'^\s*[Dd][Ee][Ss][Cc][Rr][Ii][Pp][Tt][Ii][Oo][Nn]\s([^\s]+.*)'
    IWS_VARTABLE = r'[Vv][Aa][Rr][Tt][Aa][Bb][Ll][Ee]\s+(\/[^\s]*\/)([^\s]*)'
    IWS_FREEDAYS_LINE = r'[Ff][Rr][Ee][Ee][Dd][Aa][Yy][Ss]\s+(\/[^\s]*\/)([^\s]*)(?:\s?(?:([Ss][Aa])|([Ss][Uu])))*'
    IWS_UNTIL = r'(?![Jj][Ss]|[Oo][Nn])[Uu][Nn][Tt][Ii][Ll]\s*(\d{2})(\d{2})'
    IWS_JSUNTIL = r'[Jj][Ss][Uu][Nn][Tt][Ii][Ll]\s*(\d{2})(\d{2})'
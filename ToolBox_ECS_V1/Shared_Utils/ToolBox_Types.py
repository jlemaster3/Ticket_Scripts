#-------------------------------------------------
#   Imports
#-------------------------------------------------
import re
import pyarrow as pa
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
class ToolBox_Plus_Minus_Options (StrEnum):
    PLUS = 'plus'
    MINUS = 'minus'

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
    """List of premade Regular Expressions.
    
    When used in an re.search or re.match, the results will contain named groups.

    !!! EDIT PATTERNS AT YOUR OWN RISK !!!
    """
    BLANK_LINE = r'^\s*$'
    NOTE_LINE = r'^ ?(?:#+(?![^\s]+[^!:])) ?(?P<note>.*)'
    YEAR_MONTH_DAY = r'(?P<year>\d{2,4})[-\/\.]?(?P<month>\d{2})[-\/\.]?(?P<day>\d{2,4})'
    IWS_TIMEZONE = r'(?:\s+[Tt][Zz]\s+(?P<time_zone>[^\s]*))'
    IWS_OBJECT_PATH_PARTS = r'(?P<workstation>[\/|@][^\s]+#)(?P<folder>\/[^\s]+\/)(?P<object>[^\s]+)\.(?P<sub_object>@|[^\s]+)'
    IWS_CARRYFORWARD = r'(?P<carryforward>[Cc][Aa][Rr]{2}[Yy][Ff][Oo][Rr][Ww][Aa][Rr][Dd])'
    IWS_ENV_ISOLATE = r'^\s*#{1}(?!\!)(?P<isolate_env>[^\s]*):'
    IWS_ENV_EXCLUDE = r'^\s*#{1}\!{1}\s*(?P<exclude_env>[^\s]*):'
    IWS_FD_OFFSET_OPTION = r'(?P<freeday_offset>[Ff][Dd][Nn][Ee][Xx][Tt]|[Ff][Dd][Pp][Rr][Ee][Vv]|[Ff][Dd][Ii][Gg][Nn][Oo][Rr])'
    IWS_STREAM_START_LINE = r'^\s*[Ss][Cc][Hh][Ee][Dd][Uu][Ll][Ee]\s*(?P<workstation>[\/|@][^\s]+#)(?P<folder>[^\s]*(?:[^\s]*)*\/)*(?P<stream>[^\s.*?\.]*)'
    IWS_STREAM_EDGE_LINE = r'^\s*(?P<stream_edge>:){1}'
    IWS_STREAM_END_LINE = r'^ ?(?P<end>[Ee][Nn][Dd])\b'
    IWS_DRAFT_LINE = r'(?P<draft>[Dd][Rr][Aa][Ff][Tt])'
    IWS_ON_REQUEST_LINE = r'(?P<on_request>[Oo][Nn]\s+[Rr][Ee][Qq][Uu][Ee][Ss][Tt])'
    IWS_JOB_START_LINE = r'^\s*(?P<workstation>[\/@][^\s]+#)(?P<folder>\/[^\/\s]*(?:\/[^\/\s]*)*\/)*(?P<job>[^\s.*?\.]*).*?[^\s]?([^\s@]*)?(?: [Aa][Ss] )?(?P<alias>[^\s@]*)?'
    IWS_ON_RUNCYCLE_GROUP_LINE = r'(?:[Oo][Nn])\s+(?:[Rr][Uu][Nn][Cc][Yy][Cc][Ll][Ee])\s+(?P<name>[^\s]*)\s+(:?\$[Rr][Cc][Gg])\s+(?P<folder>\/[^\s]+\/)(?P<rcg>[^\s]+)\b'
    IWS_ON_RUNCYCLE_FREQ_LINE = r'(?:[Oo][Nn])\s+(?:[Rr][Uu][Nn][Cc][Yy][Cc][Ll][Ee])\s+([^\s]*)\s+\"\s*[Ff][Rr][Ee][Qq]\s*=\s*(?P<freq>[Dd][Aa][Ii][Ll][Yy]|[Ww][Ee]{2}[Kk][Ll][Yy]|[Mm][Oo][Nn][Tt][Hh][Ll][Yy]|[Yy][Ee][Aa][Rr][Ll][Yy])\s*;\s*[Ii][Nn][Tt][Ee][Rr][Vv][Aa][Ll]=(?P<interval>[\d]*)\s*\;\s*(?P<by>[^\s]*)\s*=\s*(?P<by_list>[^\s]*)\s*\"\s*(?:[Ss][Uu][Bb][Ss][Ee][Tt]\s*(?P<subset>[^\s]+)\s+(?P<and_or>[Aa][Nn][Dd]|[Oo][Rr]))'
    IWS_ON_DAY_LINE = r'(?:[Oo][Nn])\s*(?P<day_of_week>\b(?:[Mm][Oo]|[Tt][Uu]|[Ww][Ee]|[Tt][Hh]|[Ff][Rr]|[Ss][Aa]|[Ss][Uu])\b)'
    IWS_ON_DATE_LINE = r'^\s*(?:[Oo][Nn] (?![Rr][Uu][Nn][Cc][Yy][Cc][Ll][Ee]))(?:(?P<year>\d{2,4})[\-\/\.]?(?P<month>\d{2})[\-\/\.]?(?P<day>\d{2,4}))'
    IWS_FOLLOWS_LINE = r'[Ff][Oo][Ll][Ll][Oo][Ww][Ss]\s+(?:(?P<workstation>[\/|\@][^\s]*#)(?P<folder>(?:\/[^\s]+)+\/)(?P<stream>[^.\s]+)(?:\.(?P<job>[^\s@]+|@))?|(?P<sibling>[^\s]+))'
    IWS_AT_SCHEDTIME = r'(?P<at_shedtime>[Aa][Tt]|[Ss][Cc][Hh][Ee][Dd][Tt][Ii][Mm][Ee])\s+(?P<hh>[\d]{2})?(?P<mm>[\d]{2})'
    IWS_PLUS_MINUS_DAYS = r'(?P<plus_minus>[+-])(?P<days>\d)\s+[Dd][Aa][Yy][Ss]?'
    IWS_VALIDTO = r'(?:[Vv][Aa][Ll][Ii][Dd][Tt][Oo])\s*\b(?P<year>\d{2,4})[\-\/\.]?(?P<month>\d{2})[\-\/\.]?(?P<day>\d{2,4})\b'
    IWS_VALIDFROM = r'(?:[Vv][Aa][Ll][Ii][Dd][Ff][Rr][Oo][Mm])\s*\b(?P<year>\d{2,4})[\-\/\.]?(?P<month>\d{2})[\-\/\.]?(?P<day>\d{2,4})\b'
    IWS_MATCHING_LINE = r'[Mm][Aa][Tt][Ch][Hh][Ii][Nn][Gg]\s*(?:(?P<plus_minus>[+-])\s*(?P<hour>\d{2})(?P<minutes>\d{2})|(?P<sameday_previous>[Ss][Aa][Mm][Ee][Dd][Aa][Yy]|[Pp][Rr][Ee][Vv][Ii][Oo][Uu][Ss]))'
    IWS_SAMEDAY_PREVIOUS = r'(?P<sameday_previous>[Ss][Aa][Mm][Ee][Dd][Aa][Yy]|[Pp][Rr][Ee][Vv][Ii][Oo][Uu][Ss])'
    IWS_JOIN_LINE = r'[Jj][Oo][Ii][Nn]\s+(?P<name>[^\s]*)\s*(?P<amount>\d|[Aa][Ll]+)\s*OF'
    IWS_ENDJOIN_LINE = r'(?P<endjoin>[Ee][Nn][Dd][Jj][Oo][Ii][Nn])'
    IWS_DESCRIPTION_LINE = r'[Dd][Ee][Ss][Cc][Rr][Ii][Pp][Tt][Ii][Oo][Nn]\s(?P<description>[^\s]+.*)'
    IWS_VARTABLE = r'[Vv][Aa][Rr][Tt][Aa][Bb][Ll][Ee]\s+(?P<folder>\/[^\s]*\/)(?P<vartable>[^\s]*)'
    IWS_FREEDAYS_LINE = r'[Ff][Rr][Ee][Ee][Dd][Aa][Yy][Ss]\s+(?P<folder>\/[^\s]*\/)(?P<name>[^\s]*)(?:\s?(?:(?P<saterday>[Ss][Aa])|(?P<sunday>[Ss][Uu])))*'
    IWS_UNTIL = r'(?![Jj][Ss]|[Oo][Nn])[Uu][Nn][Tt][Ii][Ll]\s*(?P<hh>\d{2})?(?P<mm>\d{2})'
    IWS_JSUNTIL = r'[Jj][Ss][Uu][Nn][Tt][Ii][Ll]\s*(?P<hh>\d{2})?(?P<mm>\d{2})'
    IWS_ONUNTIL = r'(?:\s*[Oo][Nn][Uu][Nn][Tt][Ii][Ll] (?P<onuntil>[^\s]+))'
    IWS_CONFIRMED = r'(?P<confirmed>[Cc][Oo][Nn][Ff][Ii][Rr][Mm][Ee][Dd])'
    IWS_CRITICAL = r'(?P<critical>[Cc][Rr][Ii][Tt][Ii][Cc][Aa][Ll])'
    IWS_DEADLINE = r'(?:[Dd][Ee][Aa][Dd][Ll][Ii][Nn][Ee])\s+(?:(?P<hh>\d{2})?(?P<mm>\d{2})|(?P<plus_minus>[+-])\s*(?P<days>\d+)\s+[Dd][Aa][Yy][Ss])'
    IWS_EVERY = r'(?:[Ee][Vv][Ee][Rr][Yy]\s+(?P<hh>\d{2})?(?P<mm>\d{2}))'
    IWS_EVERYENDTIME = r'(?:[Ee][Vv][Ee][Rr][Yy][Ee][Nn][Dd][Tt][Ii][Mm][Ee]\s+(?P<hh>\d{2})?(?P<mm>\d{2}))'
    IWS_RECOVERY_LINE = r'^\s*(?:[Rr][Ee][Cc][Oo][Vv][Ee][Rr][Yy]\s*(?P<option>[^\s]+))'
    IWS_AFTER = r'(?:[Aa][Ff][Tt][Ee][Rr]\s?(?P<workstation>[\/@][^\s]+#)?(?P<folder>\/?[^\s]*(?:\/[^\/\s]*)*\/)?(?P<job>[^\s]+))'
    IWS_DOCOMMAND_LINE = r'^\s*[Dd][Oo][Cc][Oo][Mm][Mm][Aa][Nn][Dd]\s*\"(?P<task>.*)\"'

#-------------------------------------------------
#   PyArrow - Structures
#-------------------------------------------------
ToolBox_Struct_Entity_Relationships:list[pa.field] = [
    pa.field('key_id', pa.string()),
    pa.field('source_entity_id', pa.string()),
    pa.field('target_entity_id', pa.string()),
    pa.field('type', pa.string())
]


ToolBox_Struct_IWS_Stream = [
    pa.field('_hash', pa.string()),
    pa.field('workstation', pa.string()),
    pa.field('folder', pa.string()),
    pa.field('name', pa.string()),
    #pa.field('description', pa.string()),
    #pa.field('draft', pa.bool_()),
    #pa.field('priority', pa.int32()),
    #pa.field('onoverlap', pa.bool_()),
    #pa.field('matching', pa.string()),
    #pa.field('freedays', pa.string()),
    #pa.field('validfrom', pa.string()),
    #pa.field('validto', pa.string()),
]

ToolBox_Struct_IWS_Job = [
    pa.field('_hash', pa.string()),
    pa.field('workstation', pa.string()),
    pa.field('folder', pa.string()),
    pa.field('name', pa.string()),
    pa.field('alias', pa.string()),
    pa.field('description', pa.string()),
    pa.field('confirmed', pa.bool_()),
    pa.field('critical', pa.bool_()),
    pa.field('nop', pa.bool_()),
    pa.field('priority', pa.int32()),
    pa.field('keyjob', pa.string()),
    pa.field('command', pa.string()),
    pa.field('logon', pa.string()),
    pa.field('tasktype', pa.string()),
    pa.field('recovery', pa.string()),
    pa.field('recovery_interval', pa.string()),
    pa.field('recovery_attempts', pa.int32()),
    pa.field('recovery_after', pa.string()),
    pa.field('abendprompt', pa.string())
]
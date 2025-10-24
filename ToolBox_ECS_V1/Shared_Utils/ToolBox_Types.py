#-------------------------------------------------
#   Imports
#-------------------------------------------------
from enum import StrEnum

#-------------------------------------------------
#   Enums
#-------------------------------------------------

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
    DEPENDENCY = 'dependency'
    IWS_JOBSTREAM = 'iws_jobstream'
    IWS_JOB = 'iws_job'
    IWS_TIMING = 'iws_timing'
    IWS_RUNCYCLE = 'iws_runcycle'
    IWS_FOLLOW = 'iws_follow'
    IWS_JOIN = 'iws_join'
    IWS_RESOURCE = 'iws_resource'
    IWS_OPENS = 'iws_opens'
    IWS_PROMPT = 'iws_prompt'
    
class ToolBox_REGEX_Patterns (StrEnum):
    BLANK_LINE = r'^\s*$'
    NOTE_LINE = r'^\s*#(?!\s*:)'
    IWS_OBJECT_PATH_PARTS = r'([/@][A-Za-z0-9_-]+#)(/[^/\s]*(?:/[^/\s]*)*/)*([^\s.*?\.]*).*?[^\s]?([^\s@]*)?'
    IWS_ENV_ISOLATE = r'#{1}([\w+]*):'
    IWS_ENV_EXCLUDE = r'#{1}!{1}([\w+]*):'
    IWS_STREAM_START_LINE = r"^\s*SCHEDULE\s*([/@][A-Za-z0-9_-]+#)(/[^/\s]*(?:/[^/\s]*)*/)*([^\s.*?\.]*)"
    IWS_STREAM_EDGE_LINE = r"^\s*(:)"
    IWS_STREAM_END_LINE = r'\s*[Ee][Nn][Dd]{1}(?![Jj][Oo][Ii][Nn])'
    IWS_STREAM_PATH_PARTS = r'^\s*SCHEDULE\s*([/@][A-Za-z0-9_]+#)(/[^/\s]*(?:/[^/\s]*)*/)[.\b]?([^\s]*).*?[^\s]?([^\s@]*)?'
    IWS_STREAM_DRAFT = r'^\s*DRAFT\s'
    IWS_STREAM_RUNCYCLE_LINE = r'ON\sRUNCYCLE'
    IWS_STREAM_ONREQUEST_LINE = r'ON\sREQUEST'
    IWS_JOB_START_LINE = r'^\s*([/@][A-Za-z0-9_-]+#)(/[^/\s]*(?:/[^/\s]*)*/)*([^\s.*?\.]*).*?[^\s]?([^\s@]*)?'
    IWS_JOB_PATH_PARTS = r'([/@][A-Za-z0-9_-]+#)(/[^/\s]*(?:/[^/\s]*)*/)*([^\s.*?\.]*).*?[^\s]?([^\s@]*)?(?: [Aa][Ss] )?([^\s@]*)?'
    IWS_RUNCYCLE_LINE = r'(?:[Oo][Nn]\s*[Rr][Uu][Nn][Cc][Yy][Cc][Ll][Ee])\s+([^\s]*)'
    IWS_RUNCYCLE_PARTS = r'((#{1}!?)([\w+]*))?:?(?:[Oo][Nn]\s*[Rr][Uu][Nn][Cc][Yy][Cc][Ll][Ee])\s+([^\s]*)(?:.*)(?:\s+([Aa][Tt]|[Ss][Cc][Hh][Ee][Dd][Tt][Ii][Mm][Ee])\s+([\d]+)).(([+-]\d+)\s+([Dd][Aa][Yy][Ss]))?'
    IWS_FOLLOWS_LINE = r'\s*[Ff][Oo][Ll][Ll][Oo][Ww][Ss]\s+(?:([@/][^/\s]*#)((?:/[^/\s]+)+/)([^./\s]+)(?:\.([^\s@]+|@))?|([^\s]+))'
    IWS_AT_SCHEDTIME = r''
    IWS_JOIN_LINE = r'\s*[Jj][Oo][Ii][Nn]\s+([^\s]*)\s*(\d|[Aa][Ll]+)\s*OF'
    IWS_ENDJOIN_LINE = r'ENDJOIN'
    IWS_DESCRIPTION_LINE = r'^\s*DESCRIPTION\s'

class ToolBox_Options (StrEnum):
    ANY = 'any'
    ALL = 'all'
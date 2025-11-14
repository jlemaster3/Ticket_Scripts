#-------------------------------------------------
#   Imports
#-------------------------------------------------
import os, copy, re
from datetime import datetime as dt

#-------------------------------------------------
#   Variables
#-------------------------------------------------

contract = 'Toolbox'
ticketNumber = 'RITM01234567'

source_path = f"C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\{contract}_{ticketNumber}\\TEST_ENV"

# Define Working Directory
working_directory = os.path.join ("C:\\Users\\jlemaster3\\OneDrive - Gainwell Technologies\\Documents\\_Ticket_Repo\\", f"{contract}_{ticketNumber}")

#-------------------------------------------------
#   Initialize Script
#-------------------------------------------------

if __name__ == "__main__":

    _regex_pattern_1:str = r'^\s*(?:[Oo][Nn] (?![Rr][Uu][Nn][Cc][Yy][Cc][Ll][Ee]))(?:(?P<year>\d{2,4})[\-\/\.]?(?P<month>\d{2})[\-\/\.]?(?P<day>\d{2,4})(?:[\s|\,])*)*'
    _regex_pattern_2:str = r"(?P<date>(?P<year>\d{2,4})[\-\/\.]?(?P<month>\d{2})[\-\/\.]?(?P<day>\d{2,4}))"

    source_file:str = os.path.join (source_path, 'PROD\\Temp_test.jil')

    _holder:str|None = None
    with open(source_file, "r", encoding="utf-8") as f:
        _holder = copy.deepcopy(f.read())

    _holder_lines = _holder.splitlines() or []

    for _line_idx, _line_str in enumerate(_holder_lines):
        _match_results = re.finditer(_regex_pattern_2, _line_str, re.IGNORECASE) 
        if _match_results is not None:
            _line_printed:bool = False
            for _m_count, _m in enumerate(_match_results):
                if isinstance(_m, re.Match):
                    if _line_printed == False:
                        print (f"[{_line_idx}] - '{_line_str}'")
                        _line_printed = True
                    for _g_count, (_g_key, _g_val) in enumerate(_m.groupdict().items()):
                        print (f"    [{_g_count}] '{_g_key}' : {type(_g_val)}  {_g_val}")
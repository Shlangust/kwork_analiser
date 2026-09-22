from parser import run_one_kwork
from agent import stack_chek
from excel import add_col


kwork_data = run_one_kwork('excemple://link')
kwork_analyzer = (kwork_data | stack_chek(kwork_data))
add_col(kwork_analyzer)
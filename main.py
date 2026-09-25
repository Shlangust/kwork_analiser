from parser import run_one_kwork, get_kwork, main_session,get_kworks
from agent import stack_chek, make_answer
from excel import add_col
from playwright.sync_api import sync_playwright


with main_session() as page:
    kworks = get_kworks(page)
    print(1)
    for kwork in kworks:
        print(2)
        kwork = kwork |stack_chek(kwork)
        print(3)
        if kwork['fits']:
            kwork = kwork | {"answer":make_answer(kwork)}
        add_col(kwork)

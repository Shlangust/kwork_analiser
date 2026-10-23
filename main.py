from parser import run_one_kwork, get_kwork, main_session,get_kworks
from agent import stack_chek, make_answer
from excel import add_col
from playwright.sync_api import sync_playwright
import time

with main_session() as page:
    kworks = get_kworks(page)
    for kwork in kworks:
        kwork = kwork |stack_chek(kwork)
        if kwork['fits']:
            kwork = kwork | {"answer":make_answer(kwork)}
        add_col(kwork)

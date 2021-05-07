from bs4 import BeautifulSoup

fo = open("ipl_2020_sechudule_html.txt", "r")
data = fo.read()

soup = BeautifulSoup(data, 'html.parser')

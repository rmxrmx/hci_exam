from numpy import number
import requests
import wikipediaapi as wp
import streamlit as st
import random

#st.set_page_config(layout="wide")
wiki_wiki = wp.Wikipedia('en')


def print_sections(sections, level=0):
        for s in sections:
                print("%s: %s - %s" % ("*" * (level + 1), s.title, s.text))


#print_sections(page_py.sections)

def print_categorymembers(categorymembers, level=0, max_level=1):
        for c in categorymembers.values():
            print("%s: %s (ns: %d)" % ("*" * (level + 1), c.title, c.ns))
            if c.ns == wp.Namespace.CATEGORY and level < max_level:
                print_categorymembers(c.categorymembers, level=level + 1, max_level=max_level)



S = requests.Session()

URL = "https://en.wikipedia.org/w/api.php"

# PARAMS = {
#     "action": "query",
#     "format": "json",
#     "list": "allcategories",
#     "aclimit": "max",
#     "acmin": 30
# }

# R = S.get(url=URL, params=PARAMS)
# DATA = R.json()
# next_cat = DATA["continue"]["accontinue"]
# cats = DATA["query"]["allcategories"]

# categories = []
# for cat in cats:
#     categories.append(cat["*"])


# while True:
#     PARAMS = {
#     "action": "query",
#     "format": "json",
#     "list": "allcategories",
#     "aclimit": "max",
#     "acmin": 30,
#     "accontinue": next_cat
#     }

#     R = S.get(url=URL, params=PARAMS)
#     DATA = R.json()
#     cats = DATA["query"]["allcategories"]

#     for cat in cats:
#         categories.append(cat["*"])

#     if "continue" in DATA:
#         next_cat = DATA["continue"]["accontinue"]
#     else:
#         break


# # print(categories)

# # Now we have all of the categories of some relevance

# translated_categories = []
# i = 0

# while i < len(categories):
#     PARAMS = {
#         "action": "query",
#         "titles": "|".join(categories[i:i+30]),
#         "prop": "langlinks",
#         "format": "json",
#         "lllimit": "max",
#         "lllang": "en"
#     }

#     R = S.get(url=URL, params=PARAMS)
#     DATA = R.json()

#     for link in DATA["query"]["pages"].values():
#         if "langlinks" in link:
#             translated_categories.append([link["title"], link["langlinks"][0]["*"]])

#     i += 30

# print(translated_categories)

# Now we have any useful categories + their translation to English





# page_extracts = []
# page_categories = []
# for title in page_titles:
#     # get extract of a page
#     PARAMS = {
#         "action": "query",
#         "format": "json",
#         "prop": "extracts",
#         "exchars": 400,
#         "exintro": True,
#         "titles": title,
#         "explaintext": True
#     }

#     R = S.get(url=URL, params=PARAMS)
#     texts = R.json()

#     page_extracts.append(list(texts["query"]["pages"].values())[0]["extract"])

#     # get categories of a page
#     PARAMS = {
#         "action": "query",
#         "format": "json",
#         "prop": "categories",
#         "titles": title,
#         "cllimit": 10,
#         "clshow": "!hidden"
#     }

#     R = S.get(url=URL, params=PARAMS)
#     categories = R.json()

#     # choose random category
#     #number_of_categories = len(list(categories["query"]["pages"].values())[0]["categories"])


#     # ignores "born in" and "died in" categories
#     cats = []
#     for cat in list(categories["query"]["pages"].values())[0]["categories"]:
#         if "Født" not in cat["title"] and "Døde" not in cat["title"]:
#             cats.append(cat["title"])

#     chosen_category = random.randint(0, len(cats) - 1)
#     page_categories.append(cats[chosen_category])


# for i in range(len(page_categories)):
#     page_categories[i] = [i, page_categories[i]]

# random.shuffle(page_categories)

# st.write(page_titles, page_extracts, page_categories)

# col1, col2, col3 = st.columns([4,2,4])

# for i, title in enumerate(page_titles):
#     with col1.expander(str(i) + ". " + title):
#         st.write(page_extracts[i])

# for i, cat in enumerate(page_categories):
#         col2.number_input("", key=i)
#         col3.write(cat[1][9:])

# TODO: remove dead and born categories...


# cat = wiki_wiki.page("Kategori:Den danske guldalder")
# print("Category members: Den danske guldalder")

# titles = []

# for c in cat.categorymembers.values():
#     # get only articles with a good number of sections
#     # if len(c.sections) >= 4 and c.ns == 0:
#     titles.append(c.title)

# # print(len(cat.categorymembers.values()), len(titles))
# random.shuffle(titles)
# # chosen = random.sample(range(len(titles)), 10)
# print(chosen)


# big_pages = []
# i = 0
# while len(big_pages) < 10 or i < len(titles):
#     page = wiki_wiki.page(titles[i])
#     if len(page.sections) >= 5 and c.ns == 0:
#         big_pages.append(page)

# @st.cache(suppress_st_warning=True)
# def create_text():

# get 10 random pages
PARAMS = {
    "action": "query",
    "format": "json",
    "list": "random",
    "rnfilterredir": "nonredirects",
    "rnlimit": 10,
    "rnnamespace": 0
}

R = S.get(url=URL, params=PARAMS)
pages = R.json()

page_titles = []

for page in pages["query"]["random"]:
    page_titles.append(page["title"])

# TODO: make this work for all of them
page = wiki_wiki.page(page_titles[0])
max_len = 0
max_section = ""
max_title = ""
for section in page.sections:
    if len(section.text) > max_len:
        max_len = len(section.text)
        max_section = section.text
        max_title = section.title
        # with st.expander(section.title):
        #     st.write(section.text)

words = max_section.split()

chosen_words = random.sample(range(len(words)), 5)
chosen_words.sort()

removed_words = [words[i] for i in chosen_words]

for i, index in enumerate(chosen_words):
    words[index] = str(i+1) + ".___"

col1, col2 = st.columns(2)
random.shuffle(removed_words)


words = " ".join(words)


col1.subheader(page.title + " / " + max_title)
col1.write(words)

form = col2.form("my_form")

for word in removed_words:
    form.number_input(word, 1, 5, step=1, format="%i", key=word)

form.form_submit_button("Submit")
# for i in chosen:
#     page = wiki_wiki.page(titles[i])

#     for section in page.sections:
#          with st.expander(section.title):
#              st.write(section.text)
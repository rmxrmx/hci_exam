from ntpath import join
from turtle import onclick
from numpy import number
import requests
import wikipediaapi as wp
import streamlit as st
import random

# index == the 10 pages for questions / answers
# page:
#   0: starting page
#   1: game page
#   2: results page
if 'index' not in st.session_state:
    st.session_state['index'] = 0
if 'page' not in st.session_state:
    st.session_state['page'] = 0
if "results" not in st.session_state:
    st.session_state["results"] = []
if "game_number" not in st.session_state:
    st.session_state["game_number"] = 0


def advance_game():
    st.session_state["page"] += 1
    if "lang" not in st.session_state:
        st.session_state["lang"] = st.session_state["language"]
    st.session_state["index"] = 0

if st.session_state["page"] == 0:
    st.title("Learning with Wikipedia!")
    st.selectbox("Language", ["en", "da", "de", "ru"], key="language")
    st.button("Start", on_click=advance_game)


if st.session_state["page"] == 1:
    language = st.session_state["lang"]
    wiki_wiki = wp.Wikipedia(language)


def print_sections(sections, level=0):
        for s in sections:
                print("%s: %s - %s" % ("*" * (level + 1), s.title, s.text))


def print_categorymembers(categorymembers, level=0, max_level=1):
        for c in categorymembers.values():
            print("%s: %s (ns: %d)" % ("*" * (level + 1), c.title, c.ns))
            if c.ns == wp.Namespace.CATEGORY and level < max_level:
                print_categorymembers(c.categorymembers, level=level + 1, max_level=max_level)



S = requests.Session()



col1, col2 = st.columns(2)

# get 10 random pages
PARAMS = {
    "action": "query",
    "format": "json",
    "list": "random",
    "rnfilterredir": "nonredirects",
    "rnlimit": 10,
    "rnnamespace": 0
}

@st.cache(allow_output_mutation=True)
def get_pages(language, number):
    URL = "https://" + language + ".wikipedia.org/w/api.php"
    R = S.get(url=URL, params=PARAMS)
    pages = R.json()
    
    page_summaries = []
    page_titles = []

    for idx, page in enumerate(pages["query"]["random"]):
        wiki_page = wiki_wiki.page(page["title"])
        # TODO: might want to do some more extensive splitting
        page_summaries.append(wiki_page.summary.split()[:200])
        page_titles.append(str(idx + 1) + ". " + page["title"])

    return page_titles, page_summaries

if st.session_state["page"] == 1:
    titles, summaries = get_pages(language, st.session_state["game_number"])


index = st.session_state['index']

@st.cache(allow_output_mutation=True)
def generate_page(index):
    words = summaries[index].copy()
    print("ran")
    chosen_words = random.sample(range(len(words)), 5)
    chosen_words.sort()

    removed_words = [words[i] for i in chosen_words]
    removed_words_index = [0, 1, 2, 3, 4]

    for i, idx in enumerate(chosen_words):
        words[idx] = "<font color='orange'>" + str(i+1) + ".\_\_\_</font>"

    random.shuffle(removed_words_index)


    joined_words = " ".join(words)

    return removed_words, removed_words_index, joined_words, words, chosen_words

if st.session_state["page"] == 1:
    removed_words, removed_words_index, joined_words, words, chosen_words = generate_page(index)


    col1.subheader(titles[index])
    col1.markdown(joined_words, True)

    form = col2.form("my_form")

    numbered_inputs = []

    for idx, element in enumerate(removed_words_index):
        form.number_input(removed_words[element], 1, 5, step=1, format="%i", key=str(index) + str(idx))

    for i in range(5):
        if str(index) + str(i) not in st.session_state:
            st.session_state[str(index) + str(i)] = 1

def update_page():
    results = 0
    for i in range(5):
        if st.session_state[str(index) + str(i)] == removed_words_index[i] + 1:
            words[chosen_words[removed_words_index[i]]] = "<font color='green'>" + removed_words[removed_words_index[i]] + "</font>"
            results += 1
        else:
            words[chosen_words[removed_words_index[i]]] = "<font color='red'>~~" + removed_words[st.session_state[str(index) + str(i)] - 1] + "~~ " + removed_words[removed_words_index[i]] + "</font>"        
    

    j_w = " ".join(words)
    st.session_state[index] = [j_w, titles[index]]

    st.session_state["results"].append(results)


    if st.session_state['index'] == 9:
        advance_game()
    else:
        st.session_state['index'] += 1

def go_back():
    st.session_state['index'] -= 1
    
def update_results_page():
    st.session_state['index'] += 1

def start_again():
    st.session_state['page'] = 0
    st.session_state['index'] = 0
    st.session_state["game_number"] += 1

if st.session_state["page"] == 1:
    if index != 9:
        submit = form.form_submit_button("Next", on_click=update_page)
    else:
        submit = form.form_submit_button("Submit", on_click=update_page)


if st.session_state["page"] == 2:

    col4, col5 = st.columns(2)

    total_score = sum(st.session_state["results"])

    col4.subheader(st.session_state[index][1])
    col4.markdown(st.session_state[index][0], True)

    col5.subheader("Results:")
    col5.write("Total score: {} / 50, or {}%".format(total_score, int(100 * total_score / 50)))

    col1, col2, col3 = st.columns([1, 1, 4])
    if st.session_state['index'] != 0:
        col1.button("Back", on_click=go_back)
    if st.session_state['index'] != 9:
        col2.button("Next", on_click=update_results_page)

    st.button("Play Again", on_click=start_again)


# TODO:

# 1. Make an intro page, where you can choose:
# language, optionally: category

# 2. in the game:
# upon submission, allow user to go through their results
# show some stats
# button to play again
# share?
# high scores?

# have a timer

# VISUAL considerations

# have something to back up your choices

# justify having only one game
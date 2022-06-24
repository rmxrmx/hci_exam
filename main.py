from ntpath import join
from turtle import onclick
from numpy import number
import requests
import wikipediaapi as wp
import streamlit as st
import random
import pandas as pd

def language_converter(lang):
    if lang == "English":
        return "en"
    elif lang == "Danish":
        return "da"
    elif lang == "German":
        return "de"
    elif lang == "Lithuanian":
        return "lt"
    elif lang == "Russian":
        return "ru"
    elif lang == "Chinese":
        return "zh"

# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """

# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)


green = "#adc178"
yellow = "#CB9F5D"
red = "#ff4d6d"
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
if "titles" not in st.session_state:
    st.session_state["titles"] = []

st.title("Learning Languages With Wikipedia")

def advance_game():
    st.session_state["page"] += 1
    if "language" in st.session_state:
        st.session_state["lang"] = language_converter(st.session_state["language"])
    st.session_state["index"] = 0

if st.session_state["page"] == 0:
    st.subheader("Instructions")
    st.write("You will be presented with 10 summaries from Wikipedia of the language of your choice. Five words from each summary will be removed, and it is your task to place them in the correct locations in the text. Select the language to train and press Start to begin.")
    
    col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 2, 1])
    col2.selectbox("Language", ["English", "Danish", "German", "Lithuanian", "Russian", "Chinese"], key="language")
    col4.button("Start", on_click=advance_game)


if st.session_state["page"] == 1:
    language = st.session_state["lang"]
    wiki_wiki = wp.Wikipedia(language)

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

@st.cache(allow_output_mutation=True, show_spinner=False)
def get_pages(language, number):
    with st.spinner("Loading..."):
        URL = "https://" + language + ".wikipedia.org/w/api.php"
        R = S.get(url=URL, params=PARAMS)
        pages = R.json()
        
        page_summaries = []
        page_titles = []

        for idx, page in enumerate(pages["query"]["random"]):
            wiki_page = wiki_wiki.page(page["title"])
            # TODO: might want to do some more extensive splitting
            page_summaries.append(wiki_page.summary.split()[:150])
            page_titles.append(str(idx + 1) + ". " + page["title"])

    return page_titles, page_summaries

if st.session_state["page"] == 1:
    titles, summaries = get_pages(language, st.session_state["game_number"])
    st.session_state["titles"] = titles


index = st.session_state['index']

@st.cache(allow_output_mutation=True)
def generate_page(index, language, number):
    words = summaries[index].copy()
    print("ran")
    chosen_words = random.sample(range(len(words)), 5)
    chosen_words.sort()

    removed_words = [words[i] for i in chosen_words]
    removed_words_index = [0, 1, 2, 3, 4]

    for i, idx in enumerate(chosen_words):
        words[idx] = "<font color='{}'>**".format(yellow) + str(i+1) + ".\_\_\_**</font>"

    random.shuffle(removed_words_index)


    joined_words = " ".join(words)

    return removed_words, removed_words_index, joined_words, words, chosen_words

if st.session_state["page"] == 1:
    removed_words, removed_words_index, joined_words, words, chosen_words = generate_page(index, language, st.session_state["game_number"])


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
            words[chosen_words[removed_words_index[i]]] = "<font color='{}'>**".format(green) + removed_words[removed_words_index[i]] + "**</font>"
            results += 1
        else:
            words[chosen_words[removed_words_index[i]]] = "<font color='{}'>**~~".format(red) + removed_words[st.session_state[str(index) + str(i)] - 1] + "~~ " + removed_words[removed_words_index[i]] + "**</font>"        
    

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
    st.session_state["results"] = []
    st.session_state["titles"] = []

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

    if total_score >= 40:
        color = green
    elif total_score <= 20:
        color = red
    else:
        color = yellow

    col5.subheader("Results:")
    col5.markdown("<p style='font-family:sans-serif; color:{}; font-size: 20px;'><strong>Total score: {} / 50, or {}%</strong></p>".format(color, total_score, int(100 * total_score / 50)), True)
    res = []

    df = pd.DataFrame(zip(st.session_state["titles"], st.session_state["results"]), columns=["Text", "Correct Answers"])#.style.highlight_between(left=1.5, right=3.5, props='font-weight:bold;color:#e83e8c')

    col5.table(df)

    col1, col2, col3 = st.columns([1, 1, 4])
    if st.session_state['index'] != 0:
        col1.button("Back", on_click=go_back)
    if st.session_state['index'] != 9:
        col2.button("Next", on_click=update_results_page)

    st.button("Play Again", on_click=start_again)


# TODO:

# 1. Make an intro page, where you can choose:


# 2. in the game:
# show some stats
# colour them?
# share?
# high scores?

# link to the page

# add a loading thing

# VISUAL considerations

# have something to back up your choices

# justify having only one game

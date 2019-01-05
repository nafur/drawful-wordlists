import random

import wiktionary

def select(words, k):
    return random.sample(words, k)

def redewendungen(k):
    return select(wiktionary.query_category("de", "Kategorie:Redewendung_(Deutsch)"), k)


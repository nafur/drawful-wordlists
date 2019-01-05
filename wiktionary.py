import json
import requests

def query(lang, params):
    r = requests.get("https://%s.wiktionary.org/w/api.php" % lang, params = params)
    data = json.loads(r.text)
    return data

def filter_words(words):
    return list(filter(
        lambda x: "Kategorie:" not in x,
        words
    ))

def query_category(lang, category):
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category,
        "format": "json",
        "cmlimit": 3000
    }
    res = []
    while True:
        result = query(lang, params)
        data = result["query"]["categorymembers"]
        data = list(map(lambda d: d["title"], data))
        res = res + data
        if not "continue" in result:
            break
        con = result["continue"]
        params["cmcontinue"] = con["cmcontinue"]
    return filter_words(res)

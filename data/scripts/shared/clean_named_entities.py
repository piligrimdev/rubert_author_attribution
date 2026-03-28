import spacy

def clean_named_entities(text: str, spacy_pkg: str = "ru_core_news_lg") -> str:
    nlp = spacy.load(spacy_pkg)

    clean_tokens = []
    doc = nlp(text)

    for t in doc:
        if t.ent_type_ in ["PER", 'LOC', 'ORG']:
            clean_tokens.append(f"[{t.ent_type_ }]")
        else:
            clean_tokens.append(t.text)
        clean_tokens.append(t.whitespace_)

    return "".join(clean_tokens).strip()

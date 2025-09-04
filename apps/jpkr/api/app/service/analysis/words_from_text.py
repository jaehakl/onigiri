import fugashi
import unidic

def extract_words_from_text(text: str):
    tagger = fugashi.Tagger('-d "{}"'.format(unidic.DICDIR))
  
    document = []
    words_dict = {}
    text_list = text.split("\n")
    for line_text in text_list:
        line = []
        line_words = tagger(line_text)
        for word in line_words:
            feat = word.feature            
            lemma_id = int(getattr(feat, "lemma_id", None)) if getattr(feat, "lemma_id", None) else None
            line.append({                
                "surface": word.surface,
                #"surface": word.surface if getattr(feat, "lemma", None) != None else " "+word.surface,
                "lemma_id": lemma_id,
            })
            if lemma_id not in words_dict:
                words_dict[lemma_id] = {
                    "lemma_id": lemma_id,
                    "lemma": getattr(feat, "lemma", None),
                    "pos1": getattr(feat, "pos1", None),
                    "pos2": getattr(feat, "pos2", None),
                    "pos3": getattr(feat, "pos3", None),
                    "pos4": getattr(feat, "pos4", None),
                    "cType": getattr(feat, "cType", None),
                    "cForm": getattr(feat, "cForm", None),
                    "lForm": getattr(feat, "lForm", None),
                    "orth": getattr(feat, "orth", None),
                    "pron": getattr(feat, "pron", None),
                    "orthBase": getattr(feat, "orthBase", None),
                    "pronBase": getattr(feat, "pronBase", None),
                    "goshu": getattr(feat, "goshu", None),
                    "iType": getattr(feat, "iType", None),
                    "iForm": getattr(feat, "iForm", None),
                    "fType": getattr(feat, "fType", None),
                    "fForm": getattr(feat, "fForm", None),
                    "iConType": getattr(feat, "iConType", None),
                    "fConType": getattr(feat, "fConType", None),
                    "type": getattr(feat, "type", None),
                    "kana": getattr(feat, "kana", None),
                    "kanaBase": getattr(feat, "kanaBase", None),
                    "form": getattr(feat, "form", None),
                    "formBase": getattr(feat, "formBase", None),
                    "aType": getattr(feat, "aType", None),
                    "aConType": getattr(feat, "aConType", None),
                    "aModType": getattr(feat, "aModType", None),
                    "lid": getattr(feat, "lid", None),
                }
        document.append(line)
        
    return document, words_dict
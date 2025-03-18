import spacy
import re
import sys, fitz
import pandas as pd
import numpy as np

"""
You can comment the code from line 10 to 23 once u have trained the model 
"""
df_resume = pd.read_csv("C:/Users/kenchatg/Softwares/Sem2/ProjInAI/InterviewAI/Resume_Parsing/Resume/Resume.csv") #Path of the Resume folder

#randomized Job categories so that 200 samples contain various job categories instead of one.
df_resume = df_resume.reindex(np.random.permutation(df_resume.index))

# limit our number of samples to 200 as processing 2400+ takes time.
df_resume = df_resume.copy().iloc[0:200,]


nlp = spacy.load("en_core_web_md")
skill_pattern_path = "C:/Users/kenchatg/Softwares/Sem2/ProjInAI/InterviewAI/Resume_Parsing/jz_skill_patterns.jsonl" #path to jz_skill_patterns.jsonl file

ruler = nlp.add_pipe("entity_ruler")
ruler.from_disk(skill_pattern_path)

def remove_hyperlinks(sentence):
    
    #just in case there is hyperlink....
    sentence = re.sub(
        '(@[A-Za-z0-9]+)|([^0-9A-Za-z /t])|(/w+://///S+)|^rt|http.+?"',
        " ",
        sentence
    )
    
    return sentence

def preprocessing(sentence):
    
    sentence = remove_hyperlinks(sentence)
    
    doc = nlp(sentence)
    cleaned_tokens = []
    for token in doc:
        # print(token.text, token.lemma_, token.pos_, token.is_stop)
        if token.is_stop == False and \
            token.pos_ != 'SYM' and \
            token.pos_ != 'PUNCT' and token.pos_ != 'SPACE':
            cleaned_tokens.append(token.lemma_.lower().strip())
            
    #instead of returning tokens, we shall join them
    return " ".join(cleaned_tokens)

# Below is the path of the dummy resume to be tested
fname = 'C:/Users/kenchatg/Softwares/Sem2/ProjInAI/InterviewAI/Resume_Parsing/Tanuj-Kenchannavar-FlowCV-Resume-20250304.pdf'
doc = fitz.open(fname)
text = ""
for page in doc:
    text = text + str(page.get_text())

tx = " ".join(text.split('/n'))
tx = preprocessing(tx)

doc = nlp(tx)
skills = [ent.text for ent in doc.ents if ent.label_ == "SKILL"]

# Print unique skills
print(set(skills))
from math import nan
from pdfminer.high_level import extract_text
import os
import re
import docx2txt
import nltk
import spacy
import locationtagger
from nltk.corpus import wordnet
import csv
from spacy.matcher import PhraseMatcher
import pprint


nlp = spacy.load('en_core_web_sm') 

custom_nlp2 = spacy.load(os.path.join("Assets","degree","model"))


file = "Assets/LINKEDIN_SKILLS_ORIGINAL.txt"
degreefile = "Assets/Degree.txt"
degreefile = open(degreefile).read().splitlines()
statefile = "Assets/states.txt"
statefile = open(statefile).readlines()
cityfile = "Assets/cities-states.csv"
csvreaderplace = csv.reader(file)
places = []
for row in csvreaderplace:
    places.append(row)


file = open(file, "r", encoding='utf-8')    
skill = [line.strip().lower() for line in file]
skillsmatcher = PhraseMatcher(nlp.vocab)
patterns = [nlp.make_doc(text) for text in skill if len(nlp.make_doc(text)) < 10]
skillsmatcher.add("Job title", None, *patterns)


#-----------------------------------------------------------

PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')

csv_file = open('csv_data.csv', 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Name', 'Email', 'PhoneNumber', 'Qualification',
                    'Experience (Yes/No)', 'City', 'field of expirence'])


def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)


def extract_text_from_docx(docx_path):
    txt = docx2txt.process(docx_path)
    if txt:
        return txt.replace('\t', ' ')
    return None

#-----------------------------------------------------------

def find_names(String):
    Sentences = nltk.sent_tokenize(String)
    Tokens = []
    for Sent in Sentences:
        Tokens.append(nltk.word_tokenize(Sent)) 
    Words_List = [nltk.pos_tag(Token) for Token in Tokens]

    Nouns_List = []

    for List in Words_List:
        for Word in List:
            if re.match('[NN.*]', Word[1]):
                Nouns_List.append(Word[0])

    Names = []
    for Nouns in Nouns_List:
        if not wordnet.synsets(Nouns):
            Names.append(Nouns)

    return Names

def find_highest_qualification(qualifications):
    for deg in degreefile:
        for qual in qualifications:
            if qual.startswith(deg):
                return qual
    
    return ' '.join(qualifications)


def extract_phone_number(cv_data):
    phonenumber = PHONE_REG.search(cv_data)
    try:
        return phonenumber.group()
    except:
        return None

def extract_emails(cv_data):
    #return re.findall(EMAIL_REG, resume_text)
    email = EMAIL_REG.search(cv_data)
    try:
        return email.group()
    except:
        return None


def extract_city(cv_data):
    
    try:
        place_entity = locationtagger.find_locations(text=cv_data)
        place = (place_entity.cities)[0]
    except:
        place = None
    return place


def extract_state(text):
    #TODO change it if u want
    states =[]

    text = (text.split(" "))
    text2 = []
    for words in text:
        word = words.split("\n")
        text2+=word
    text+=text2
    for words in text:
        word = words.split(",")
        text2+=word
    text+=text2
    for i in range(len(text)):
        text[i] = text[i].strip()
        for state in statefile:
            state = state.strip()
            if state.lower() == text[i].lower() and state != '':
                states.append(state)
    if states  == []:
        return None
    else:
        return states[0]

def extract_skills(text):
        skills = []
        __nlp = nlp(text.lower())

        matches = skillsmatcher(__nlp)
        for match_id, start, end in matches:
            span = __nlp[start:end]
            skills.append(span.text)
        skills = list(set(skills))
        return skills


def get_degree(text):
    doc = custom_nlp2(text)

    degree = (ent.text.replace("\n", " ") for ent in list(doc.ents) if ent.label_ == 'Degree')
    degree= set(dict.fromkeys(degree).keys())

    text = text.split("\n")

    for i in range(len(text)):
        text[i] = text[i].strip()
        for deg in degreefile:
            if deg in text[i] and deg != '':
                degree.add(deg)

    if not degree:
        return None

    return degree


def check_expirence(text):
    if "Experience" in text or "EXPERIENCE" in text:
        return True
    else:
        return False

data={}
text = ""
for filename in os.listdir('files'):
    if filename.endswith('.docx'):
        text = extract_text_from_docx("files/"+filename)
    elif filename.endswith('.pdf'):
        text = extract_text_from_pdf("files/"+filename)
        if text == "":
            print(f"Couldn't extract text from {filename}")
            continue
    else:
        continue
    
    names = find_names(text)
    phone_number = extract_phone_number(text)
    emails = extract_emails(text)
    city = extract_city(text)
    skills = extract_skills(text)
    degree = get_degree(text)
    if check_expirence(text):
        expirence = "Yes"
    else:
        expirence = "No"

    state = extract_state(text)
    
    if city != None and state!=None:
        city = city+","+state
    elif state != None:
        city = state
    else:
        if state == None and city == None:
            city = ''
    if skills == []:
        skills = ''
    if degree != None:
        highest_degree = find_highest_qualification(degree)
        if not highest_degree:
            highest_degree = degree
    else:
        highest_degree = ''

    n = []
    not_char = re.compile('[^0-9a-zA-Z]+')
    for name in names:
        if not any(map(str.isdigit, name)) and not (not_char.search(name)) and name[0].isupper():
            if name.lower() not in skills and name not in city:
                n.append(name)

    names = n
    if names != []:
        try :
            name = names[0]+" "+names[1]
        except:
            name = names[0]
    else:
        name = ''
        

    print(n) 

    data= {
        "name": name,
        "ph" : phone_number,
        "email":emails,
        "city":city,
        "skills":skills,
        "degree":degree,
        "expirence":expirence,
        "highest_degree": highest_degree
    }

    exp = ""
    if skills != None:
        for i in skills:
            exp = exp + i + ", "
    else:
        exp = None

    deg = ""
    if degree != None:
        for i in degree:
            deg = deg + i + ", "
    else:
        deg = None

    pprint.pprint(data)
    print("----------------------------------------------------------------------------------------------")

    csv_writer.writerow([data["name"], data["email"], data['ph'], data["highest_degree"] , expirence, data['city'], exp])

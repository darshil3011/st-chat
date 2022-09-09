import streamlit as st
from streamlit_chat import message
import requests
import spacy 
import pickle
from bs4 import BeautifulSoup as bs
import re
from lxml import etree
import pandas as pd

with open('rail_chatbot.pkl', 'rb') as f:
    vect, model = pickle.load(f)

#nlp = spacy.load("saved_model/")

st.set_page_config(
    page_title="Streamlit Chat - Demo",
    page_icon=":robot:"
)

st.header("Chatbot")
st.markdown("NLP Chatbot with Named Entity Recognition")

if 'train' not in st.session_state:
    st.session_state.train = ''

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []
    
def chat(text):
    test_dtm = vect.transform([text])
    intent = model.predict(test_dtm)
    
    return intent

def train_info(train_no):
    # CODE FOR TRAIN COACH & TRAIN DEPARTURE,ARRIVAL 
    
    url = "https://www.trainman.in/coach-position/" + str(train_no)
    response = requests.get(url)
    soup = bs(response.content, 'html.parser') 
    rev_div = soup.findAll("div",attrs={"class","text-justify mx-3 ng-star-inserted"}) 
    coach_line = []
    for j in range(len(rev_div)):
    # finding all the p tags to fetch only the review text
        coach_line.append(rev_div[j].find("b").text)
    #print("Coach::",coach_line)

    #code for departed station
    url_trainstatus = "https://www.railmitra.com/live-train-running-status/" + str(train_no)
    trainstatus_response = requests.get(url_trainstatus)
    soup_train = bs(trainstatus_response.content, 'html.parser') 
    trainstatus_rev_div = soup_train.findAll("div",attrs={"class","card cardResult"})
    trainstatus_rev_div = str(trainstatus_rev_div)
    # print("trainstatus_rev_div:",trainstatus_rev_div)
    departure_station = re.search(r'from<strong>(.*?)</strong>', trainstatus_rev_div).group(1)
    #print("Departed From :",departure_station)

    #code for arrival station
    navigation = soup_train.findAll("div",attrs={"class","well well-sm"})
    dummy_arrstation = navigation
    navigation = str(navigation)
    arr_station = soup_train.findAll("div",attrs={"class","col-7 col-md-4"})
    arr_station = str(arr_station)
    arrival_station = re.search(r'<div class="col-7 col-md-4"><span class="ind-crossed"><i aria-hidden="true" class="fa fa-circle-thin"></i></span>(.*?)</div>',arr_station).group(1)
    #print("Arrival_station at :",arrival_station)

    #code for platform details like arrival time, departed time,haukt and platform number
    url_trainstatus = "https://www.trainman.in/train/"+str(train_no)
    trainstatus_response = requests.get(url_trainstatus)
    soup_train = bs(trainstatus_response.content, 'html.parser') 
    dom = etree.HTML(str(soup_train))
    newdetail = soup_train.findAll("tr",attrs={"class","ng-star-inserted"})
    newdetail = str(newdetail)
    station_list = []    
    for i in range(1,100):
        current_list = []
        n2 = dom.xpath('/html/body/app-root/app-wrapper/div/main/train-schedule/div[2]/div[1]/div/div[3]/table/tbody/tr['+ str(i) +']/td[2]/strong/text()')
        t2 = dom.xpath('/html/body/app-root/app-wrapper/div/main/train-schedule/div[2]/div[1]/div/div[3]/table/tbody/tr['+ str(i) +']/td[3]/div[1]/time/text()')
        d2 = dom.xpath('/html/body/app-root/app-wrapper/div/main/train-schedule/div[2]/div[1]/div/div[3]/table/tbody/tr['+ str(i) +']/td[3]/div[2]/time/text()')
        h2 = dom.xpath('/html/body/app-root/app-wrapper/div/main/train-schedule/div[2]/div[1]/div/div[3]/table/tbody/tr['+ str(i) +']/td[4]/time/text()')
        p2 = dom.xpath('/html/body/app-root/app-wrapper/div/main/train-schedule/div[2]/div[1]/div/div[3]/table/tbody/tr['+ str(i) +']/td[7]/text()')

        current_list.append(n2) #add name of station
        current_list.append(t2) #add arrival time
        current_list.append(d2) #add departure time
        current_list.append(h2) #add hault duration
        current_list.append(p2) #add platform number
        
        if len(n2) != 0 :
            station_info = {'name' : n2, 'arrival' : t2, 'departure' : d2, 'hault' : h2, 'platform' : p2}

        elif len(n2) == 0:
            break

        station_list.append(station_info)
        
    return coach_line, departure_station, arrival_station, station_list

def get_text():
    input_text = st.text_input("You: ","Hello !", key="input")
    return input_text 

def get_train():
    text_input_container = st.empty()
    #train = text_input_container.text_input("Enter train no:")
    #if train != '':
    #    text_input_container.empty()
    train = text_input_container.selectbox(
     'Select train no',
     ('00000 - I am not travelling', '12932 - Double Decker Express', '12901 - Gujarat Mail'))
    if train != '00000 - I am not travelling':
        text_input_container.empty()
    train = train[0:5]
    return train

def get_loc():
    text_input_container = st.empty()
    location = text_input_container.text_input("Enter current station:")
    if location != '':
        text_input_container.empty()
    
    return location
      

user_input = get_text()

if user_input:
   
    
    intent = chat(user_input)
  
    if intent == 0 or intent == 2: 
        response = "I am your travel partner. I can answer all your queries related to train journey. Lets start with your train name and PNR no."
        train_no = get_train()
        st.session_state.train = train_no
        if train_no != '00000':
            response = 'I am your travel partner. I can answer all your queries related to train journey. Lets start with your train name and PNR no. Your train no is ' + str(train_no)

    elif intent == 1: 
        response = "We are available 24/7 to help you. Reach out to us on +91.9999 9999 or email us at enquire@thinkinbytes.in"
            
    elif intent == 3:
        response = "Ok, great. What can I do for you ?"
        
    elif intent == 4: 
        train_input = st.session_state.train
        coach_line, departure_station, arrival_station, station_list = train_info(int(train_input))
        location = get_loc()
        for i in station_list:
            if location in str(i).lower():
                output = i
        #station_table = pd.DataFrame.from_dict(station_list, orient='columns')
        response = str(output)

    elif intent == 5:
        response = "hmmm.. what else ?" 
    
    elif intent == 6:
        response = "glad that I helped you. Bye ! Take care." 
    
    elif intent == 7: 
        train_input = st.session_state.train
        coach_line, departure_station, arrival_station, station_list = train_info(int(train_input))
        response = "It seems you need help to reach your coach position. Here is the coach lineup for your train:" + str(coach_line)  

    elif intent == 8:
        train_input = st.session_state.train
        coach_line, departure_station, arrival_station, station_list = train_info(int(train_input))
        response = "Your train has departed from "+str(departure_station)+" and will arrive to "+str(arrival_station) 
        
    elif intent == 9:
        response = "Unfortunately I cant do that for you right now !"

    elif intent == 10:
        response = "Here are few emergency contacts : Railway Enquiry : 139, Railway Police : 182, Accident and Safety : 1072, IRCTC Tourism : 1800 110 139" 

    elif intent == 11:
        response = "Your PNR status is : booking confirmed, seat no S4/18 (LB) -  chart prepared" 
        
    elif intent == 12:
        train_input = st.session_state.train
        coach_line, departure_station, arrival_station, station_list = train_info(int(train_input))
        
        response = " train info :"                 

    if st.session_state.generated != '':
        st.session_state.past.append(user_input)
        st.session_state.generated.append(response)

if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')


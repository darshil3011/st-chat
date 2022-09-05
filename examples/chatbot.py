import streamlit as st
from streamlit_chat import message
import requests
import spacy 
import pickle

with open('chatbot.pkl', 'rb') as f:
    vect, model = pickle.load(f)

nlp = spacy.load("saved_model/")

st.set_page_config(
    page_title="Streamlit Chat - Demo",
    page_icon=":robot:"
)

#API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
#headers = {"Authorization": st.secrets['api_key']}

st.header("Streamlit Chat - Demo")
st.markdown("[Github](https://github.com/ai-yash/st-chat)")

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []
    
def chat(text):
    test_dtm = vect.transform([text])
    intent = model.predict(test_dtm)
    
    return intent

def get_text():
    input_text = st.text_input("You: ","Hello, how are you?", key="input")
    return input_text 

def get_train():
    text_input_container = st.empty()
    train = text_input_container.text_input("Enter train no:")
    return train

user_input = get_text()

if user_input:
    
    intent = chat(user_input)
  
    if intent == 0:
        response = "Teksun is a product based as well as service based company. We provide services across different domains like firmware, AI, web & app development etc"

    elif intent == 1:
        response = "We are available 24/7 to help you. Reach out to us on +91.9999 9999 or email us at help@teksun.com"

    elif intent == 2:
        response = "We can customise our existing products to cater your requirements or build something from scratch for you."

    elif intent == 3:
        response = "Hey, nice to meet you ! I am Teksun Bot. What is your name?"

    elif intent == 4:
        response = "Ok, great. What can I do for you ?"

    elif intent == 5:
        
        doc = nlp(user_input)
        for i in doc.ents:
            
            if i.label_ == 'product':
                if 'fire' in i.text.lower() or 'smoke' in i.text.lower():
                    response = "fire & smoke detection is available !"
                elif 'game' in i.text.lower() or 'gamification' in i.text.lower():
                    response = "AI gamification is available !"
                elif 'safety gear' in i.text.lower() or 'gear' in i.text.lower():
                    response = "Safety Gear detection is available !"
                elif 'intrusion' in i.text.lower():
                    response = "Intrusion detection available !"
                elif 'occupancy' in i.text.lower():
                    response = "Car occupancy and occupancy detection available !"
                elif 'tejas' in i.text.lower() or 'tejas care' in i.text.lower():
                    response = "Teksun Tejas is available !"
                elif 'teksun telep' in i.text.lower() or 'telep' in i.text.lower():
                    response = "Telep solutions available !"
                elif 'driver' in i.text.lower() and 'monitor' in i.text.lower():
                    response = 'Driver monitoring system available !'
                elif 'fall detection' in i.text.lower():
                    response = 'Fall detection system available !'
                elif 'train detection' in i.text.lower():
                    train_no = get_train()
                    response = 'Your train no is ' + str(train_no)
                    text_input_container.empty()
    
                    
    elif intent == 6:
        response = "hmmm ok"

    elif intent == 7:
        response = "See you later ! Visit again. Glad to meet you"
         
    st.session_state.past.append(user_input)
    st.session_state.generated.append(response)

if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')


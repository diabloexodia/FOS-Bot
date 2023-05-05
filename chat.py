import random
import json
import Paraphraser
import Inverted_Indexing
import torch
import sys
# from Paraphraser import paraphrase
import pyttsx3
import Speech
import speech_recognition as sr
import Query_Indexing
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
import summarizer

engine = pyttsx3.init()
r = sr.Recognizer()

def get_response():
    FILE = "data.pth"
    data = torch.load(FILE, map_location=torch.device('cpu'))

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


    with open('intents.json', 'r') as json_data:
        intents = json.load(json_data)

    

    input_size = data["input_size"]
    hidden_size = data["hidden_size"]
    output_size = data["output_size"]
    all_words = data['all_words']
    tags = data['tags']
    model_state = data["model_state"]

    model = NeuralNet(input_size, hidden_size, output_size).to(device)
    model.load_state_dict(model_state)
    model.eval()

    

    bot_name = "FOS"
    print(f"{bot_name}:Let's chat! (Type 'Quit' to exit)")
    Speech.SpeakText("Let's chat! FOS at your service")

    with open('C:/Users/Diablo/Desktop/Chatbot_Beta-FOS_BOT--main/prtext.txt', 'r') as file:
     paraphrased_text=file.read()
    with open('C:/Users/Diablo/Desktop/Chatbot_Beta-FOS_BOT--main/summ.txt', 'r') as file:
     text = file.read()


    while True:
        
        # Create a recognizer object
        r = sr.Recognizer()

        # Start recording the speech
        with sr.Microphone() as source:
          print("Speak now...")
          audio = r.listen(source)

    # Convert speech to text
        # print(sentence)
        # sentence = r.recognize_google(audio)
        try:
         sentence = r.recognize_google(audio)
         print("You said:", sentence)
        except sr.UnknownValueError:
         print("Could not understand audio.")
         continue
        except sr.RequestError as e:
         print("Could not request results from Google Speech Recognition service; {0}".format(e))
         continue

            
        

        sentence = tokenize(sentence)
        X = bag_of_words(sentence, all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X).to(device)

        output = model(X)
        _, predicted = torch.max(output, dim=1)

        tag = tags[predicted.item()]
        #print(tag)
        
        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()]

        if sentence in ["quit", "exit","goodbye"]:
         print(random.choice(intents['goodbye']['responses']))
         sys.exit() 

        if prob.item() > 0.75:

            if tag == "Paraphrase":
               
               with open('C:/Users/Diablo/Desktop/Chatbot_Beta-FOS_BOT--main/prtext.txt', 'r') as file:
                paraphrased_text=file.read()

               print(f"{bot_name}: " + paraphrased_text)
               engine.say(paraphrased_text)
               engine.runAndWait()
               continue


            if tag == "Summarizer":
          
                multiline_string=text
                summ = summarizer.Summarizer()
                summ.set_text(multiline_string)
                summarized_text = summ.summarize()
                print(f"{bot_name}: " + summarized_text)
                engine.say(summarized_text)
                engine.runAndWait()
                continue


            if tag == "Inverted Index":
                multiline_string=text
                index = Inverted_Indexing.Indexing()
                sent = index.Index(multiline_string)
                if sent is not None:
                 print(f"{bot_name}: " + sent)

                engine.say(sent)
                engine.runAndWait()
                continue


            if tag == "Query retrieval":
             
                multiline_string=text
                query = Query_Indexing.Query()
                print("I have processed the document/paragraph")
                while True:
                 question  = input(f"{bot_name}:  Shoot your questions lad I am here to help \n")
                 if question in["stop","end"] :
                    break
                 if question ==".":
                    with sr.Microphone() as source:
                     print("Speak now...")
                     audio = r.listen(source)
                     question = r.recognize_google(audio)
                    print("You said:", question)
                    answer = query.generate_answer(question,multiline_string)
                    print(f"{bot_name}: " + answer)
                    engine.say(answer)
                 engine.runAndWait()
                continue
        
            for intent in intents['intents']:
                if tag == intent["tag"]:
                    response = random.choice(intent['responses'])
                    print(f"{bot_name}: " + response)
                    engine.say(response)
                    engine.runAndWait()
        else:
            Speech.SpeakText(f"{bot_name}: I do not understand...")

          

get_response()
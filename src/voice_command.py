#python 3+ only
"""
        By  : Al Sabawi
            : 01/03/2011
        
"""
import platform
import speech_recognition as sr
from gtts import gTTS
import pyttsx3

import wikipediaapi
import os
import sys
import requests
import json
import time
import re
import urllib
import html2text
import logging
import tempfile
from playsound import playsound
import webtext
import time
import traceback


PLATFORM = platform.system()
OS_RELEASE = platform.release()
MYLOCATION = None
CURR_DIR = os.path.dirname(os.path.realpath(__file__))

WAKEUP_WORD = 'samantha'
MYVOICES = {'pico':'rebecca','pyttsx':'simon','gtts':'samantha','espeak':'amanda'} # Values are : gtts, pyttsx, espeak
CURRENT_VOICE = 'gtts'
# CURRENT_VOICE = 'pico'
RECOGNIZER = 'google'

recog = sr.Recognizer()
mic = sr.Microphone()

pytts = pyttsx3.init()
pyttsVolume = pytts.getProperty('volume')
pytts.setProperty('volume', 1.25)
pyttsRate = pytts.getProperty('rate')
pytts.setProperty('rate', 180)
pytts.setProperty('voice', 'english')

logger = logging.getLogger('voice_log')

def chunk_text(text,max = 199):
    text = text.replace("\"","'")
    chunks = []
    
    while max != -1 and len(text) > max:
        # Find the last whitespace character before index max
        i = text.rfind('.', 0, max)
        # If no whitespace character was found, break at index max
        if i == -1:
            i = max
        # Add the chunk to the list of chunks and remove it from the text
        chunks.append(str(text[:i]).strip())
        text = text[i+1:]
    # Add the final chunk to the list of chunks
    chunks.append(str(text).strip())
    return chunks

def wikioedia_query(question):
    question=str(question.strip())
    print(question)

    # Create Wikipedia API object
    wiki = wikipediaapi.Wikipedia('en')
    
    # Define regular expression pattern to match a question
    pattern = r"^(?:what|who|when|where|why|how)(?:\s+(?:is|are|was|were|will|can|could|should|would))?\s+(.+?)(?:[\s\?])?$"

    # # Take user input as question
    # question = str(text)

    # Apply pattern to the question
    match = re.match(pattern, question.lower())

    if match:
        # Replace the matched text with the corresponding query string
        query = match.group(1)
        query = query.strip()
    else:
        # If no pattern matches, use the original question as the query
        query = question.strip()

    # Search Wikipedia for the query
    print(f"q = {query}")
    page = wiki.page(query)
    
    # Print the summary of the Wikipedia page
    if page.exists():
        return page.summary.replace("\"","'")+" That's it for "+query
    else:
        return "Sorry, I couldn't find anything on that topic."

def get_forecast(lat, lon):
    # Get the grid endpoint for the provided coordinates
    response = requests.get(f"https://api.weather.gov/points/{lat},{lon}")
    if response.status_code == 200:
        grid_data = response.json()
        grid_url = grid_data['properties']['forecast']
        # Get the forecast data for the grid endpoint
        response = requests.get(grid_url)
        if response.status_code == 200:
            forecast_data = response.json()
            # Extract the relevant forecast information
            forecast_periods = forecast_data['properties']['periods']
            forecast = ''
            for period in forecast_periods:
                forecast += f"{period['name']}: {period['detailedForecast']}\n"
            return forecast
        else:
            return f"Error retrieving forecast data: {response.status_code}"
    else:
        return f"Error retrieving grid data: {response.status_code}"

def testVoices(pytts):
    rate = pytts.getProperty('rate')
    volume = pytts.getProperty('volume')
    voice = pytts.getProperty('voice')

    print (rate)
    print (volume)
    print (voice)

    newVoiceRate = 50
    while newVoiceRate <= 300:
        print ('Rate = {0}'.format(newVoiceRate))
        pytts.setProperty('rate', newVoiceRate)
        pytts.say('Testing different voice rates.')
        pytts.runAndWait()
        pytts.setProperty('rate', newVoiceRate)
        newVoiceRate += 50

    newVolume = 0.1
    while newVolume <= 2:
        print ('Volume = {0}'.format(newVoiceRate))
        pytts.setProperty('volume', newVolume)
        pytts.say('Testing different voice volumes.')
        pytts.runAndWait()
        newVolume = newVolume + 0.3


def setLogger():
    global logger
    # logging.basicConfig(filename='voicedebug.log', encoding='utf-8', level=logging.DEBUG)
    hdlr = logging.FileHandler('./voicelog.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    

def changeVoice():
    global CURRENT_VOICE
    global WAKEUP_WORD
    i = 1
    voiceRespond('who should I change to? valid choices are:')
    for x,y in MYVOICES.items():
        if len(MYVOICES) == i:
            voiceRespond('or '+ y)
        else:
            voiceRespond(y+',')

    try:
        with mic as source:
            audio = recog.listen(source)

        value = recognizeAudio(audio,RECOGNIZER)
        if value:
            lvalue = value.lower()
            print('Human: '+lvalue)
            success = False
            for idx,v in MYVOICES.items():
                if(v == lvalue):
                    CURRENT_VOICE = idx
                    WAKEUP_WORD = v
                    voiceRespond('from now on you can call me ' + v)
                    pytts.setProperty('name', WAKEUP_WORD)
                    success = True
            if not success:
                voiceRespond(lvalue + ' is not a valid choice!')
    except sr.RequestError:
        pass
    except sr.UnknownValueError:
        pass
    except sr.URLError:
        pass

def getText(htmldata):
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_tables = True
    h.ignore_emphasis = True
    h.skip_internal_links = True

    retText = ''
    retTextLines =  h.handle(htmldata).splitlines()
    for x in retTextLines:
        if x[:4] == '===>': continue
        if x[:7] == 'Source:': break
        else: retText += ' '+x

    return retText

def saveMyLocationToFile():
    try:
        response = requests.get('https://api64.ipify.org?format=json').json()
        ip_address = response["ip"]
        jresponse = requests.get(f'https://ipapi.co/{ip_address}/json/').json()

        with open('geodata.json', 'w', encoding='utf-8') as f:
            json.dump(jresponse, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"@saveMyLocationToFile() Error from {__name__}")
        logging.error(traceback.format_exc())
        jresponse = None
        pass
    
    return jresponse


def getMyLocation():
    try:
        filename = 'geodata.json'
        f = open(filename)
    except IOError:
        logging.error(f"@getMyLocation() I/O error: {filename} Not Found")
        j = None
    else:  
        data = json.load(f)
        # Closing file
        f.close()  
        j = data
        lat = j['latitude']
        long = j['longitude']
        city = j['city']
        country = j['country_name']
        postal = j['postal']
    
    return j


def shuttingDown():
    print('Shutting Down! Goodbye')
    voiceRespond('Shutting down. Goodbye')
    sys.exit(0)

def recognizeAudio(audio,bywho=RECOGNIZER):

    value = ''
    try:
        if(bywho == 'google'):
            value = recog.recognize_google(audio).lower()
        elif(bywho == 'bing'):
            value = recog.recognize_bing(audio,).lower()
        elif(bywho == 'sphinx'):
            value = recog.recognize_sphinx(audio,"en-US").lower()
        elif(bywho == 'ibm'):
            value = recog.recognize_ibm(audio).lower()
        elif(bywho == 'wit'):
            value = recog.recognize_wit(audio).lower()
        else:
            logger.error('Unknown engine : ' + bywho)

    except sr.WaitTimeoutError:
        print('Timed out! Repeat request')
        logger.error("@recognizeAudio Http Communication Error: Possible internet outage. Msg:'{0}'".format(sr.WaitTimeoutError))

    except sr.RequestError:
        print('Timed out! Repeat request')
        logger.error("@recognizeAudio Http Communication Error: Possible internet outage. Msg:'{0}'".format(sr.RequestError))

    return value

def listen2User():
    sys.stdout.write('.')
    sys.stdout.flush()
    success = False
    while not success:
        try:
            with mic as source:
                audio = recog.listen(source)

            value = recognizeAudio(audio,RECOGNIZER)
            if value:
                print('Human: '+value.lower())
                success = True

            sys.stdout.write('+')
            sys.stdout.flush()
        except sr.RequestError:
            pass
        except sr.UnknownValueError:
            pass
        except sr.URLError:
            pass

    return value

def text2Voice(line,bywho = CURRENT_VOICE):
    try:
        if(bywho == 'gtts'):
            chunks = chunk_text(line,max=5000)
            for i in range(len(chunks)):
                tts = gTTS(text=str(chunks[i]), lang='en')
                temp = tempfile.NamedTemporaryFile(suffix='.mp3')
                try:
                    tts.write_to_fp(temp)
                except Exception as inst:
                    logger.error('Engine : ' + bywho + ':Error: ')
                    logger.error(inst)
                    logger.error(chunks[i])
                    pass
                
                temp.flush()
                #print(PLATFORM.lower())
                if PLATFORM.lower() == 'linux':
                    os.system("mpg321 -q " + temp.name)
                if PLATFORM.lower() == 'windows':
                    playsound(temp.name)
                
                temp.close()
        elif(bywho == 'pyttsx'):
            pytts.say(line)
            pytts.runAndWait()
        elif(bywho == 'espeak'):
            os.system("espeak -p30 -ven-us+f4 -s150 \"" + line.replace('"','\\') + "\"")
        elif(bywho == 'pico'):
            temp = tempfile.NamedTemporaryFile(suffix='.wav')
            os.system(f"pico2wave -l='en-US' -w={temp.name} \"" + line.replace('"','\\') + "\" 2> /dev/null")
            temp.flush()
            os.system(f"aplay {temp.name} 2> /dev/null")
            temp.close()

    except requests.exceptions.ConnectionError:
        logger.error ( 'voiceRespond() : Exception: requests.exceptions.ConnectionError encountered')

def voiceRespond(line):
        print(WAKEUP_WORD + ': ' + line)
        text2Voice(line, CURRENT_VOICE)


def adjust4Noise():
    #with m as source: recog.adjust_for_ambient_noise(source)
    with mic as source:
        recog.dynamic_energy_threshold=True
        recog.dynamic_energy_adjustment_damping = 0.15
        recog.dynamic_energy_adjustment_ratio = 1.4
        recog.energy_threshold = 250
        recog.adjust_for_ambient_noise(source)

def challengeRequest(line):
    voiceRespond('I heard ' + line + '. Is that correct?')
    value = listen2User()

    if value == 'yes' \
            or value == 'correct' \
            or value == 'yeah' \
            or value == 'yep' \
            or value == 'please' \
            or value == 'sure' \
            or value == 'affirmative' \
            or value == 'of course' \
            or value == 'positive' \
            or value == 'yes mam' \
            or value == 'ok' \
            or value == 'yes sir':
        return True
    else:
        return False

def concatenate_to_end(list,start):
    result= ''
    i = 0
    for element in list:
        if i >= start:
            result += str(element)
    return result

def processInput(line):
    global WAKEUP_WORD
    global MYLOCATION
    
    # voiceRespond("you asked me : "+line)
    first_word = line.split(' ', 1)[0]
    if(first_word == WAKEUP_WORD):
        line.split(' ', 1)

    # Process basic commands
    if line == 'shut down' or \
                    line == 'kill yourself' or \
                    line == 'die' or \
                    line == 'end program' or \
                    line == 'exit program' or \
                    line == 'bye bye':
        shuttingDown()

    elif line == 'hello' or line == 'hello '+MYVOICES[CURRENT_VOICE]:
        voiceRespond('hello there')
    elif line == 'who are you' or line == 'what\'s your name':
        voiceRespond('I am '+WAKEUP_WORD)
    elif line == 'thank you':
        voiceRespond('you are welcome')
    elif line == 'how are you':
        voiceRespond('I am fine. Thank you')
    elif line == 'calculate':
        voiceRespond('I can only perform simple arithmetics like 534 plus 127 or 126 divided by 6')
        voiceRespond('Use the word "Calculate" followed by the arithmetic operation please ')
    elif (line.split(' ', 1)[0] == 'calculate'):
        calc = line.split(' ', 1)[1]
        print (calc)
        try:
            a = eval(calc)
            voiceRespond(calc + ' equals {0}'.format(a))
        except:
            voiceRespond('I do not understand. Try saying it in a different way')
            
    elif (line == "latest news" or 
        line == "what\'s the latest news" or 
        line == "the latest news" or 
        line == "what\'s up" or 
        line == "news" or 
        line == "news please" or 
        line == "read the latest news" or 
        line == "what is the latest news") :
        voiceRespond("Working to get you the latest news, this\'ll take only few seconds ")
        voiceRespond(f"Here is the latest news from the web: {webtext.get_headlines()}")
        voiceRespond("And that wraps the news for now")
        
    elif (line.split(' ', 1)[0] == 'google'):
        if len(line.split()) == 1:
            voiceRespond("Nothing to google, try again")
        else:
            q = line.split(' ',1)[1]
            voiceRespond(f'googling {q}')
            q = q.replace("\'","%27")
            q2 = q.replace(' ', '+')
            os.system('google-chrome https://www.google.com/search?q='+q2+'> /dev/null 1> /dev/null 2> /dev/null &')
    elif line.lower().find('ask wikipedia') != -1:
        line2 = line.replace('ask wikipedia',' ')
        voiceRespond('asking wikipedia ')
        if len(line2.strip(' ')) == 0:
            voiceRespond('what\'s the question?')
            question = listen2User()
            res = wikioedia_query(question)
            line2 = question
        else:
            res = wikioedia_query(line2)
        voiceRespond(res+' '+line2)
    elif line.split(' ', 1)[0] == 'launch' or line.split(' ', 1)[0] == 'open' :
        if len(line.split(' ',1)) > 1:
            program = line.split(' ',1)[1].replace(' ', '')
            voiceRespond('launching '+ program)
            os.system(f"gnome-terminal -- bash -c '{program}; exec bash' "+ ' 1> /dev/null 2> /dev/null &')
        else:
            voiceRespond("say the word launch or open followed by the application name to run it")
            
    elif line == "query my location" or \
        line == 'update my location' or \
        line == 'query your location' or \
        line == 'check your location' or \
        line == 'update your locatio' or \
        line == "check my location":
        voiceRespond("checking my location, this may take a second")
        MYLOCATION = saveMyLocationToFile()
        if MYLOCATION:
            voiceRespond("Done! I refreshed my location")
        else:
            voiceRespond("Location query failed")
        
    elif line == 'play music':
        voiceRespond('playing music on youtube.com')
        os.system('google-chrome https://www.youtube.com/watch?v=rYEDA3JcQqw&list=RDEMTPfPURSbYpb0YHCKyIG37Q' + '> /dev/null 1> /dev/null 2> /dev/null &')
    elif line == 'get my location' or \
            line == 'get your location' or \
            line == 'where am i' or \
            line == 'where are we' or \
            line == 'where are you' or \
            line == 'location':
        voiceRespond('getting location ')
        if MYLOCATION:
            myloc = MYLOCATION
        else:
            myloc = MYLOCATION = getMyLocation()
            
        voiceRespond('We are in ' + myloc['city']+' '+myloc['region'] + ' ' + myloc['country_name'])
    elif line == "weather report" or \
        line == "what's the weather like" or \
        line == "what is the weather like" or \
        line == "the weather report" or \
        line == "the weather today" or \
        line == "what's the weather" or \
        line == "forecast" or \
        line == "weather forecast" or \
        line == "what's the forecast" or \
        line == "what's the weather forecast" or \
        line == "what's the weather like today" or \
        line == "I need the weather" :
        MYLOCATION = getMyLocation()
        if MYLOCATION:
            voiceRespond("getting the weather from US NWS, It'll be a second")
            forecast = get_forecast(lat = MYLOCATION['latitude'], lon = MYLOCATION['longitude'])
        else:
            voiceRespond("sorry, my location is unknown. I need to update my location before I can get the weather")
            forecast = None
        if forecast:
            voiceRespond(f"here is the weather forecast for {MYLOCATION['city']} as of now:" + chunk_text(forecast,max=300)[0])
            
    elif line == 'rename yourself':
        voiceRespond('what should i call myself?')
        strs = listen2User()
        voiceRespond(strs)
        WAKEUP_WORD = strs
    elif line == 'change your voice':
        changeVoice()
    else:
        q2 = line.replace(' ', '+')
        with urllib.request.urlopen('http://start.csail.mit.edu/justanswer.php?query='+q2) as response:
            content = response.read().decode('utf-8')
            text = getText(content)
            voiceRespond(text)

def wait2wakeup():
    wakeup = False
    try:
        while True:
            try:
                adjust4Noise()
                value = listen2User()
                wc = len(value.split())
                first_word = value.split(' ', 1)[0]
                if (first_word == WAKEUP_WORD):
                    wakeup = True
                    # Remove the first word
                    if wc > 1 :
                        value = value.split(' ', 1)[1]
                    else:
                        value = ''
                elif value == 'who are you' or value == "what's your name":
                    voiceRespond('I am ' + WAKEUP_WORD)
                elif value == 'hello ' + MYVOICES[CURRENT_VOICE]:
                    voiceRespond('hello there! to ask me a question, say my name followed by a question like "what is today\'s date"')

                if wakeup == True and value == '':
                    print('Oh! My name was called')
                    voiceRespond('How can I help you')
                    return True,''
                else:
                    if wakeup and not value == '':
                        return True, value

            except sr.UnknownValueError: #Timeout
                return False,''

    except KeyboardInterrupt:
        print("Shutting Down!")
        shuttingDown()

######################### Main ###################
try:
    #testVoices(pytts)

    setLogger()
    print('On '+PLATFORM+' Release : '+ OS_RELEASE)
    print("A moment of silence, please...")
    mic_list = mic.list_microphone_names()
    print(mic_list)

    adjust4Noise()
    voiceRespond('Hello, I am '+WAKEUP_WORD+'. I am now listening ')

    # Get a user voice line
    while True:
        # Wait for the wakeup word
        awake = False
        while not awake: #If timed out keep re-trying
            try:
                awake,line = wait2wakeup()
                
            except KeyboardInterrupt:
                print('Shutting down!')
                sys.exit(0)
                
        try:
            if(awake == True and line == ''):
                line = listen2User()

            processInput(line)

        except sr.UnknownValueError:
            logger.error("Oops! Didn't catch that")

        except sr.RequestError as e:
            logger.error("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))

except KeyboardInterrupt:
    pass

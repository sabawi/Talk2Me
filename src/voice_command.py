#python 3+ only
import platform
import speech_recognition as sr
from gtts import gTTS
import pyttsx3

import os
import sys
#from nltk.tokenize import sent_tokenize, word_tokenize
import requests
import json
import time
import re
import urllib
import html2text
import logging
import tempfile
from playsound import playsound

PLATFORM = platform.system()
OS_RELEASE = platform.release()

CURR_DIR = os.path.dirname(os.path.realpath(__file__))

WAKEUP_WORD = 'samantha'
MYVOICES = {'pyttsx':'simon','gtts':'samantha','espeak':'amanda'} # Values are : gtts, pyttsx, espeak
CURRENT_VOICE = 'gtts'
RECOGNIZER = 'google'

recog = sr.Recognizer()
mic = sr.Microphone()

pytts = pyttsx3.init()
pyttsVolume = pytts.getProperty('volume')
pytts.setProperty('volume', 1.25)
pyttsRate = pytts.getProperty('rate')
pytts.setProperty('rate', 160)
pytts.setProperty('voice', 'english')

logger = logging.getLogger('voice_log')

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
    hdlr = logging.FileHandler('./voicelog.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.WARNING)

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
    #retText = re.sub('<[^>]*>', ' ', htmldata)
    #retText = ''.join(xml.etree.ElementTree.fromstring(htmldata).itertext())
    p = re.compile(r'<.*?>')
    #retText = p.sub('' , htmldata)
    #print(retText.strip())
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

    #print (retText)

    return retText

def getMyLocation():
    send_url = 'http://freegeoip.net/json'
    r = requests.get(send_url)
    j = json.loads(r.text)

    #print(json.dumps(j, indent=4, sort_keys=True))
    lat = j['latitude']
    long = j['longitude']
    city = j['city']
    region = j['region_name']
    country = j['country_name']
    postal = j['zip_code']
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
        logger.error("Http Communication Error: Possible internet outage. Msg:'{0}'".format(sr.WaitTimeoutError))

    except sr.RequestError:
        print('Timed out! Repeat request')
        logger.error("Http Communication Error: Possible internet outage. Msg:'{0}'".format(sr.RequestError))

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
        #print("my current voice is " + MYVOICES[CURRENT_VOICE])
        if(bywho == 'gtts'):
            tts = gTTS(text=line, lang='en')
            temp = tempfile.NamedTemporaryFile(suffix='.mp3')
            tts.write_to_fp(temp)
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

    first_word = line.split(' ', 1)[0]
    if(first_word == WAKEUP_WORD):
        line.split(' ', 1)

    #words = word_tokenize(line)
    #i = 0
    #count = len(words)
    #voiceRespond('You used words like ')
    # while i < count:
    #     voiceRespond(words[i])
    #     i += 1

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
    elif (line.split(' ', 1)[0] == 'calculate'):
        calc = line.split(' ', 1)[1]
        print (calc)
        try:
            a = eval(calc)
            voiceRespond(calc + ' equals {0}'.format(a))
        except:
            voiceRespond('I am do not understand. Try saying it in a different way')

    elif (line.split(' ', 1)[0] == 'google'):
        q = line.split(' ',1)[1]
        q2 = q.replace(' ', '+')
        print(q2)
        os.system('google-chrome https://www.google.com/search?q='+q2+' &')

    elif line == 'play music':
        os.system('google-chrome https://www.youtube.com/watch?v=rYEDA3JcQqw&list=RDEMTPfPURSbYpb0YHCKyIG37Q' + ' &')
    elif line == 'get my location' or \
            line == 'where am i' or \
            line == 'where are we' or \
            line == 'location':
        myloc = getMyLocation()
        voiceRespond('We are in ' + myloc['city'] + ' ' + myloc['region_name'] + ' ' + myloc['country_name'])
    elif line == 'rename yourself':
        voiceRespond('what should i call myself?')
        str = listen2User()
        voiceRespond(str)
        WAKEUP_WORD = str
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
                #print ("Awake = {0} Line = {1}".format(awake,line))
            except KeyboardInterrupt:
                print('Shutting down!')
                sys.exit(0)
        try:
            if(awake == True and line == ''):
                line = listen2User()

            #if challengeRequest(line):
                # yes
                #voiceRespond('processing')
            processInput(line)
            #else:
            # no
            #voiceRespond('I can\'t help you. Sorry!')
            #voiceRespond('Say another command')

        except sr.UnknownValueError:
            logger.error("Oops! Didn't catch that")
            #voiceRespond('Did someone say something? I didn\'t catch that.')
            #adjust4Noise()
        except sr.RequestError as e:
            logger.error("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))

except KeyboardInterrupt:
    pass

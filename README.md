# Talk2Me
## Interactive Voice Interface 

### To run in the `./src` directory
```
$ python3 voice_command.py
```

Start chatting away by voice only and find out the responses. **There is no text prompt.** 
### Things you can ask are:

- **"samantha, what's the latest news"** or 
- **"samantha, where is Ottawa"** or 

### If the voice agent is set to 'rebecca',

- **"rebecca, where are we"** or 
- **"rebecca, ask Wikipedia who is Isaac Newton"** or
- **"rebecca, how far is the moon"**

When your request contains the phrase **"ask wikipedia"** in it, the code will attempt to use Wikipidia as the source

### To change the voice agent, say 
- **"samantha, change your voice"**

Remenber, this is not an AI bot, it simply uses speech-recognition to formulate text from your voice and submits it in a form of a query to open and free sites as url requests.  It then reverses the process once an answer is received using a variaty of text to speech libraries. 
Once it starts talking **you have to let it finish before you ask the next question**.

### Voice Agents
The interface comes with multiple voice agents:
- samantha
- amanda
- simon
- rebecca
The current defaul is now set to 'samantha' it might change in later updates. Don't get attached to her;)

To start a conversation, you must preface your request with the active name above for it to "wake up" and recognize what you say is a request to the program.

### To Shutdown the program

Just say the same of the agent, e.g. sanamtha, rebecca, or whichever the active agent is, followed by the words 
-**'shut down'** or 
-**'end program'** or 
-**'exit program'** or simply 
-**'bye bye':**

## Note:
There is a local log I created `voicelog.log` which I used while debugging only.  It's not active and only use it if you are debugging.  It uses the imported `logging` library for this.  Also, remember that the url requests DO NOT send any information about your computer to anyone.  

Enjoy!


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

The current default is now set to 'samantha' it might change in later updates. Don't get attached to her;)

To start a conversation, you must preface your request with the active name above for it to "wake up" and recognize you are making a request to the program.

### Common Requests
The list is growing, but here are some common requests:
- 'samantha what's the latest news' : Will read the latest headlines from NY Times, CBS News, CNBC News, and CNN News
- 'samantha ask wikipedia who is sherlock holmes' : Wll query wikipedia with key words "sherlock holmes" and read the response. Note that you must include the phrase 'ask wikipedia' for the query to go to wikipedia
- 'samantha google how to make the best spaghetti sauce' : If you use 'google' at the start of the request, it will open your web browser and search google for the best sauce, but it will Not read it!
- 'samantha launch firefox' : Will start firefox web browser. You can use the key words 'launch' or 'open' to start an application on your system
- 'samantha what is the distance between earth and the moon' : Will query the MIT knowledge database for an answer and read it
- 'samantha calculate 527 multiplied by 600' : Using the key word 'calculate' followed by arithmetic operation, it will read out the answer
- 'samantha open terminal' : This will launch a new application instance of 'terminal' or any other application. 
- 'samantha play music' : currently will only open youtube music, this maybe changed later to be the deault music player on your system
- stay tuned for more to come


### To Shutdown the program
To shut down, say the agent's name, e.g. sanamtha, rebecca, followed by the words 
-**'shut down'** or 
-**'end program'** or 
-**'exit program'** or simply 
-**'bye bye':**

## Note:
There is a local log I created `voicelog.log` which I used while debugging only.  It's not active and only use it if you are debugging.  It uses the imported `logging` library for this.  Also, remember that the url requests DO NOT send any information about your computer to anyone.  

Enjoy!


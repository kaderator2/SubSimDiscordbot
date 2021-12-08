import os, random, json
import discord
from simpletransformers.language_generation import LanguageGenerationModel

#Set help message
help = """Commands:
```
!ooc                ~ Sends a message without activting the bot
!r, !reset          ~ Resets short term memory
!modelshow          ~ Shows the active model
!modellist          ~ Shows list of all available models
!modelswitch $MODEL ~ Switches bot to specified model
!pause, !unpause    ~ Pauses/Resumes the bot
```
"""

try:
    db = json.load(open("config.json"))
except:
    raise "Failed to open config file!"

#Set variables from config file
TOKEN = db["token"]
PATH_TO_MODELS = db["models"]
DEDICATED_CHANNEL_NAME = db["channelName"]
USE_CUDA = db["useCuda"]
EXPERIMENTAL_MEMORY = db["useMemory"]
EXPERIMENTAL_MEMORY_LENGTH = db["memoryLength"]

global ACTIVE_MODEL
ACTIVE_MODEL = PATH_TO_MODELS[0]

client = discord.Client()
@client.event
async def on_ready():

    print(f'{client.user.name} has connected to Discord!')

memory = ''

def genCleanMessage(optPrompt):
        global memory
        global ACTIVE_MODEL
        formattedPrompt = '<|sor|>' + optPrompt + '<|eor|><|sor|>'
        memory += formattedPrompt
        print('\nPROMPT:' + formattedPrompt + '\n')
        print('\nMEMORY:' + memory + '\n')
        model = LanguageGenerationModel("gpt2", ACTIVE_MODEL, use_cuda=USE_CUDA)
        text_generation_parameters = {
			'max_length': 50,
			'num_return_sequences': 1,
			'prompt': memory,
			'temperature': 0.8, #0.8
			'top_k': 40,
	}
        output_list = model.generate(prompt=memory, args=text_generation_parameters)
        response = output_list[0]
        response = response.replace(memory, '')
        i = 0
        cleanStr = ''
        print(response)
        for element in response:
            if element == '<':
                i = 1
            if i == 0 and element != '!':
                cleanStr += element
            if element == '>':
                i = 0
        if not cleanStr:
            cleanStr = 'Idk how to respond to that lol. I broke.'
        memory += cleanStr + "<|eor|>"
        return cleanStr
stop = False
@client.event
async def on_message(message):
    global ACTIVE_MODEL
    global stop
    if message.author == client.user:
        return
    if str(message.channel) == DEDICATED_CHANNEL_NAME:
        if message.content == '!pause' or message.content == '!unpause':
            stop = not stop
            if stop == True:
                msgTxt = "```Paused```"
            else:
                msgTxt = "```Unpaused..```"
            await message.channel.send(msgTxt)
            return
        elif message.content == '!quit' and str(message.author.id) == '714583473804935238':
            await message.channel.send('I am quitting in order for my creator to make me better!')
            exit()
        elif message.content == '!help':
            await message.channel.send(help)
            return
        elif message.content == '!r' or message.content == '!reset':
            global memory
            memory = ''
            await message.channel.send('```convo reset```')
            print(memory)
            return
        elif message.content == '!model':
            await message.channel.send('```Im currently running a r/' + ACTIVE_MODEL + ' model!```')
            return
        elif message.content == '!modellist':
            msg = "```Heres a list of models you can use:\n"
            for i in range(len(PATH_TO_MODELS)):
                msg += str(i) + " : r/" + PATH_TO_MODELS[i] + "\n"
            msg = msg + "```"
            await message.channel.send(msg)
            return
        elif message.content.startswith("!modelswitch"):
            index = message.content
            index = index.split()
            try:
                index = int(index[1])
                ACTIVE_MODEL = PATH_TO_MODELS[index]
                status = '```Switched to r/' + ACTIVE_MODEL + '!```'
                memory = ''
                await message.guild.me.edit(nick=str(ACTIVE_MODEL.lstrip('models/') + ' bot'))
            except:
                status = "```Oops.. Looks like that didnt work. Try again```"
            await message.reply(status)
            return
        elif not stop and not message.content.startswith("!ooc "):
            if (len(memory) > EXPERIMENTAL_MEMORY_LENGTH) or (not EXPERIMENTAL_MEMORY):
                memory = ''
            async with message.channel.typing():
                prompt = message.content
                genMessage = genCleanMessage(prompt)
            return await message.reply(f"[{ACTIVE_MODEL.lstrip('models/')}] {genMessage}", mention_author=False)
        elif message.content == 'raise-exception':
            raise discord.DiscordException
    else:
        return
client.run(TOKEN)

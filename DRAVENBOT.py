# bot.py
import os
import random
from simpletransformers.language_generation import LanguageGenerationModel
import discord

TOKEN = '' #Put your token Here!
PATH_TO_MODELS = ["Pokemon", "draven", "okbuddyretard", "DutchBot", "tulpas_v2", "Sociopath"] #Put the path to your model here!
global ACTIVE_MODEL
ACTIVE_MODEL = PATH_TO_MODELS[0]
DEDICATED_CHANNEL_NAME = 'gpt2-discord-bots' #Put the name of the channel in your server where you want the bot to chat!

#Make false if you dont want to use ur gpu.
USE_CUDA = True
#CUDA cuts generation time in half. Make sure you follow github page if you want to set this to True.

'''Experimental Memory Feature! Tacks the previous responses into one big string to give the bot more context.
Might cause processing times to go up'''
EXPERIMENTAL_MEMORY = True
EXPERIMENTAL_MEMORY_LENGTH = 500 #Max char length before memory resets. Higher numbers can heavily affect model inference times. Default 500

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
    if message.content == '!pause' and str(message.channel) == DEDICATED_CHANNEL_NAME:
        stop = not stop
        if stop == True:
            msgTxt = "```Paused```"
        else:
            msgTxt = "```Unpaused..```"
        await message.channel.send(msgTxt)
        return
    if message.content == '!help' and str(message.channel) == DEDICATED_CHANNEL_NAME:
        await message.channel.send('```Commands:\n~!r~ resets short term conversation memory\n~!model~ Shows the active model\n~!modellist~ Shows list of all available models\n~!modelswitch #~ Switches bot to specified model\n~!pause~ Pauses/Resumes the bot```')
        return
    if message.content == '!r' and str(message.channel) == DEDICATED_CHANNEL_NAME:
        global memory
        memory = ''
        await message.channel.send('```convo reset```')
        print(memory)
        return
    if message.content == '!model' and str(message.channel) == DEDICATED_CHANNEL_NAME:
        await message.channel.send('```Im currently running a r/' + ACTIVE_MODEL + ' model!```')
        await message.guild.me.edit(nick=str('r/' + ACTIVE_MODEL + ' bot'))
        return
    if message.content == '!modellist' and str(message.channel) == DEDICATED_CHANNEL_NAME:
        msg = "```Heres a list of models you can use:\n"
        for i in range(len(PATH_TO_MODELS)):
            msg += str(i) + " : r/" + PATH_TO_MODELS[i] + "\n"
        msg = msg + "```"
        await message.channel.send(msg)
        return
    if '!modelswitch' in message.content.lower():
        index = message.content
        index = index.split()
        try:
            index = int(index[1])
            ACTIVE_MODEL = PATH_TO_MODELS[index]
            status = '```Switched to r/' + ACTIVE_MODEL + '!```'
            memory = ''
            await message.guild.me.edit(nick=str('r/' + ACTIVE_MODEL + ' bot'))
        except:
            status = "```Oops.. Looks like that didnt work. Try again```"
        await message.channel.send(status)
        return
    if str(message.channel) == DEDICATED_CHANNEL_NAME and not stop:
        if (len(memory) > EXPERIMENTAL_MEMORY_LENGTH) or (not EXPERIMENTAL_MEMORY):
            memory = ''
        async with message.channel.typing():
            prompt = message.content
            genMessage = genCleanMessage(prompt)
        await message.channel.send(genMessage)
    elif message.content == 'raise-exception':
        raise discord.DiscordException

client.run(TOKEN)

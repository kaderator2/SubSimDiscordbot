# bot.py
import os
import random
from simpletransformers.language_generation import LanguageGenerationModel
import discord

TOKEN = 'REPLACEME' #Put your token Here!
PATH_TO_MODEL = "REPLACEME" #Put the path to your model here!
DEDICATED_CHANNEL_NAME = 'REPLACEME' #Put the name of the channel in your server where you want the bot to chat!

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
        formattedPrompt = '<|sor|>' + optPrompt + '<|eor|><|sor|>'
        if (len(memory) == 0):
            formattedPrompt = '<|soss|><|sot|>' + optPrompt + '<|eot|><|sor|>'
        memory += formattedPrompt
        print('\nPROMPT:' + formattedPrompt + '\n')
        print('\nMEMORY:' + memory + '\n')
        model = LanguageGenerationModel("gpt2", PATH_TO_MODEL, use_cuda=USE_CUDA)
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

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == '!r' and str(message.channel) == DEDICATED_CHANNEL_NAME:
        global memory
        memory = ''
        await message.channel.send('```convo reset```')
        print(memory)
        return
    if str(message.channel) == DEDICATED_CHANNEL_NAME:
        if (len(memory) > EXPERIMENTAL_MEMORY_LENGTH) or (not EXPERIMENTAL_MEMORY):
            memory = ''
        prompt = message.content
        genMessage = genCleanMessage(prompt)
        await message.channel.send(genMessage)
    elif message.content == 'raise-exception':
        raise discord.DiscordException

client.run(TOKEN)

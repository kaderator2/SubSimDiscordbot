# bot.py
import os
import random
from simpletransformers.language_generation import LanguageGenerationModel

import discord
from dotenv import load_dotenv
load_dotenv()
TOKEN = 'haha u thought'



client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')


memory = ''

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == '!r':
        global memory
        memory = ''
        await message.channel.send('```convo reset```')
        print(memory)
        return
    if str(message.channel) == 'leauge-of-draven':
    #if 'draven' in message.content:
        if len(memory) > 1000:
            memory = ''
        model = LanguageGenerationModel("gpt2", "best_model3", use_cuda=False, args={'fp16': False})
        prompt = message.content
        prompt += '<|sor|>'
        #prompt = prompt.replace('draven ', '')
        memory += prompt
        print('\nPROMPT:' + prompt + '\n')
        print('\nMEMORY:' + memory + '\n')
        text_generation_parameters = {
			'max_length': 50,
			'num_return_sequences': 1,
			'prompt': memory,
			'temperature': 0.8, #0.8
			'top_k': 40,
			'truncate': '<|eo',
	}
        #prompt=None, 
        output_list = model.generate(prompt=memory, args=text_generation_parameters)
        response = output_list[0]
        response = response.replace(memory, '')
        memory += ' '
        for element in response:
            if element != '!':
                memory += element
        memory += ' '
        #memory += response + ' '
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
        await message.channel.send(cleanStr)
    elif message.content == 'raise-exception':
        raise discord.DiscordException

client.run(TOKEN)

#output_list = model.generate(prompt=prompt, args=text_generation_parameters)
#output_list[0]

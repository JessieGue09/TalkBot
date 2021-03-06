import random

# used for api calls
import requests

# regex
import re

# core discord.py library
import discord 

# py file containing sensitive information (CLIENT_ID, OWNER_ID)
import secrets

# Google Text-to-Speech library for TTS commands
from gtts import gTTS

# static ASCII faces and response strings
from static import FACES
from static import RESPONSES

voice_client = None

tareas = ['Buy Candy.',
            'Walk the Dog.', 
            'Take a Pen.', 
            'Love other people.']
try:
    with open ('tasklist.txt') as f:
        tareas = f.readlines()
except:
    #f = open('tasklist.txt')

    with open('tasklist.txt', 'w') as f:
        for item in tareas:
            f.write("%s\n" % item)

class TalkBot(discord.Client):
    async def on_ready(self):
        print('Connected as')
        print(self.user.name)
        print('id: {}'.format(self.user.id))
        print('------')

        # use these to display a current game being played
        # game = discord.Game("Game Title")
        # await client.change_presence(activity=game)

    async def on_message(self, message):

        # allow voice client to be used across different commands
        global voice_client

        # ensure the bot does not reply to itself
        if message.author.id == self.user.id:
            return

        # regex to return a "Hi, I'm Dad!" joke to users who use I'm, I am, etc.
        reg_search = re.search(r'(i\'m|im|i am) (.{1,})$', message.content, re.IGNORECASE)

        if reg_search:
            await message.channel.send('Hi {0}, I\'m a super Bot! {1.author.mention}'.format(reg_search.group(2), message))

        # if user @bot
        if self.user.id in message.raw_mentions:
        

            #split_msg = message.content.split()
            #split_msg = 'Hey i can speek!'.split()
            

            split_msg = [
                '@TalkBot',
                'tts'
                
            ]

            # Create homework list to add in the split_msg list
            #tareas = tareasejmp.split()
            split_msg.extend(' ')
            #split_msg.extend([t.split() for t in tareas])
            #for t in tareas:
            #    split_msg.extend(t.split())
            

            # return a randomized magic 8-ball style response along with an ASCII face
            if message.content.endswith('?'):
                await message.channel.send(
                    '{0} {1} {2.author.mention}'.format(random.choice(RESPONSES), random.choice(FACES), message))
            
            elif 'help' in message.content:
                await message.channel.send('Hello, you can use the command add "your task", to add a task in the list \n '
                'If you need to look at the task use "show my list" \n '
                'Dont forget to call the bot with @TalkBot \n '
                'if you check a fact, talk to the bot with "give me a fact" \n '
                'Mention your name with "I am" \n '
                'Question the bot if its alive with "Are you alive?". \n '
                'Thanks!')
                await message.channel.send(
                    '{0} {1.author.mention}'.format(random.choice(FACES), message))
            elif 'give me a fact' in message.content: 

                response = requests.get('https://uselessfacts.jsph.pl/random.json?language=en')

                if response.status_code != 200:

                    await message.channel.send('The uselessfacts API messed up. Yikes.')
                else:

                    await message.channel.send('{0} - Courtesy of https://uselessfacts.jsph.pl {1.author.mention}'.format(response.json()['text'], message))

            elif len(split_msg) > 2 and split_msg[2] == 'add':
                addtask = " ".join(split_msg[3:])
                tareas.append(addtask)
                
                with open('tasklist.txt', 'a') as f:
                    for addtask in tareas:
                        f.write("%s\n" % addtask)
            
            elif 'show my list' in message.content:

                for t in tareas:
                    split_msg.extend(t.split())

                # play audio via GTTS of the user's message
                if len(split_msg) > 2 and split_msg[1] == 'tts':
                    

                    # TODO: use bytestream object instead of saving .mp3 locally
                    tts = gTTS(" ".join(split_msg[2:]), 'com.au')
                    tts.save('tts.mp3')

                    if voice_client:
                        await voice_client.disconnect()

                    try:
                        channel = message.author.voice.channel
                    except AttributeError:
                        await message.channel.send('User is not in accessible voice channel!')

                    voice_client = await channel.connect(reconnect=False)
                    audio_source = await discord.FFmpegOpusAudio.from_probe('tts.mp3')
                    voice_client.play(audio_source)

                    await message.channel.send('Playing TTS in {}'.format(channel))

                    # TODO: add text limit/allow a stop command while bot is speaking
                    # disconnect voice when bot is finished speaking
                    while voice_client.is_playing():
                        continue
                    await voice_client.disconnect()
                    await message.channel.send('Left channel.')
                
             # force bot to leave vc if it is stuck
            elif message.content.lower().endswith('leave vc'):
                try:
                    await voice_client.disconnect()
                    await message.channel.send('Forced left voice channel.')
                except AttributeError:
                    await message.channel.send('I do not seem to be in a voice channel right now.')

            # only allow owner to disconnect the bot
            elif message.content.lower().endswith('disconnect') and str(message.author.id) == secrets.OWNER_ID:
                await message.channel.send('Bye bye.')
                await client.close()


if __name__ == '__main__':

    client = TalkBot(activity=discord.Activity(type=discord.ActivityType.listening,
                                               name="King Gizzard and the Lizard Wizard - Cyboogie"))

    client.run(secrets.TOKEN_ID)

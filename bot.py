from re import I
from discord.ext import commands
import discord
import json
import datetime
import datamanage
import os

version = "CBT TEST"
activity = discord.Activity(type=discord.ActivityType.watching, name=version)

bot = commands.Bot(command_prefix="w!", activity=activity)
token = open("token.txt").read()
importinfo = json.load(open("import.json", "r"))
channel = importinfo["channelid"]
owner = importinfo["owner"]

checkmsg = None
tempSubject = None


@bot.event
async def on_ready():
    print("test")


@bot.event
async def on_reaction_add(reaction, user):
    global checkmsg
    global tempSubject
    print(checkmsg)
    print(user.id)
    if reaction.message.id == checkmsg:
        if reaction.emoji == "👍" and user.id == owner:
            checkmsg = None

            subjectFile = open("data/subjectlist.txt", "a", encoding="UTF-8")
            subjectFile.write(f"\n{tempSubject}")

            await reaction.message.channel.send(f"{tempSubject}\n추가 완료")
            tempSubject = None


@bot.command()
async def write(ctx, subject=None, content=None):

    if subject == None:
        await ctx.send("주제 번호 입력")
        return
    else:
        try:
            subject = int(subject)
        except:
            await ctx.send("주제 숫자로 입력")
            return
        subtext = CheckSubject(subject)[1]

        if subtext == "존재하지 않는 주제 번호":
            await ctx.send(subtext)
            return

        if content == None:
            await ctx.send(f"{subtext} 내용 입력")
        else:
            if content[0] == "^" and content[-1] == "^":

                print(content)

                content = content.replace("^", "")
                print(content)

                if len(content) > 30:
                    await ctx.send("30자 미만으로 작성해주세요.")
                    return

                ctime = datetime.datetime.now()

                year = ctime.year
                month = ctime.month
                day = ctime.day

                hour = ctime.hour
                minute = ctime.minute
                second = ctime.second

                sendtext = f"```\n{year}-{month}-{day}-{hour}-{minute}-{second}\n"
                sendtext += f"{subtext}\n"
                sendtext += f"{content}```"

                datamanage.write(subject, ctx.author.id, content)

                await bot.get_channel(channel).send(sendtext)
            else:
                await ctx.send('''"^(내용)^"''')
                return


@bot.command()
async def read(ctx, subject=None, postno=None):
    count = 0

    if subject == None:
        await ctx.send(f"현재 주제 {CheckSubject()}개")
        return
    else:
        if subject == "all":
            sfile = open("data/subjectlist.txt", "r", encoding="UTF-8")
            await ctx.send("현재 토론중인 주제들\n" + sfile.read())
            return
        subtext = CheckSubject(subject)[1]

        if subtext == "존재하지 않는 주제 번호":
            await ctx.send(subtext)
            return

        if postno == None:

            for f in os.listdir("./data/"):
                if f.startswith(f"S{subject}P"):
                    count += 1
            await ctx.send(f"{subtext}의 글 개수 : {count}개")
        else:
            try:
                post = open(f"data/S{subject}P{postno}", "r", encoding="UTF-8")
                content = post.readlines()
                await ctx.send(content[0] + subtext + "\n" + content[2])
            except:
                if postno == "all":
                    file_list = os.listdir("data/")
                    file_list_py = [
                        file
                        for file in file_list
                        if file.endswith(".disbo") and file.startswith(f"S{subject}P")
                    ]

                    sendtext = f"{subtext}에 대한 의견들\n"
                    for i in file_list_py:
                        print(i)
                        fi = open("data/" + i, "r", encoding="UTF-8")
                        sendtext += fi.readlines()[2]
                    await ctx.send(sendtext)
                else:
                    await ctx.send("존재하지 않는 글")


def CheckSubject(subno=None):

    sublist = open("data/subjectlist.txt", "r", encoding="UTF-8").readlines()

    if subno == None:
        return len(sublist)

    if int(subno) > len(sublist):
        return False, "존재하지 않는 주제 번호"
    else:
        return True, sublist[int(subno) - 1]


@bot.command()
async def addsubject(ctx, subject=None):
    global checkmsg
    global tempSubject

    if subject == None:
        await ctx.send("주제를 입력해주세요")
        return

    if ctx.author.id == owner:
        checkmsg = await ctx.send(f"이 주제가 맞습니까?\n{subject}")
        checkmsg = checkmsg.id
        print(checkmsg)
        tempSubject = subject
    else:
        await ctx.send("봇의 관리자만 주제를 추가할수 있습니다.")


bot.run(token)

import re
from discord.ext import commands
import discord
import json
import datetime
import datamanage
import os
import pymysql
import string
import math
import random
import urllib.request as ul

version = "CBT TEST"
activity = discord.Activity(type=discord.ActivityType.watching, name=version)

bot = commands.Bot(command_prefix="w!", activity=activity)
token = open("token.txt").read()
importinfo = json.load(open("import.json", "r"))
channel = importinfo["channelid"]
owner = importinfo["owner"]

checkmsg = None
tempSubject = None


sqlinfo = open("mysql.json", "r")
sqlcon = json.load(sqlinfo)

database = pymysql.connect(
    user=sqlcon["user"],
    host=sqlcon["host"],
    db=sqlcon["db"],
    charset=sqlcon["charset"],
    password=sqlcon["password"],
    autocommit=True,
)
cur = database.cursor()


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

            sql = f"insert into subjectlist(subjectname) values ({tempSubject})"
            cur.execute(sql)

            await reaction.message.channel.send(f"{tempSubject}\n추가 완료")
            tempSubject = None


def CheckRegist(id):
    sql = f"select count(*) from userlist where userid={id}"
    cur.execute(sql)
    result = cur.fetchone()[0]

    return result


@bot.command()
async def profile(ctx, mode=None):
    if mode == "me":
        sql = f"select * from userlist where userid={ctx.author.id}"
        cur.execute(sql)
        result = cur.fetchone()
        await ctx.message.author.send(
            f"{result[2]}point level{result[3]} 마지막 출석 : {result[4]} 정지여부 : {result[5]}"
        )
    elif mode == "random":
        sql = f"select * from userlist order by rand() limit 1"
        cur.execute(sql)
        result = cur.fetchone()

        await ctx.send(
            f"{result[2]}point level{result[3]} 마지막 출석 : {result[4]} 정지여부 : {result[5]}"
        )
    else:
        await ctx.send("random or me")


@bot.command()
async def write(ctx, subject=None, content=None):
    if CheckRegist(ctx.author.id) == 0:
        await ctx.send("가입을 해주세요")
        return

    sql = f"select canwrite from userlist where userid={ctx.author.id}"
    cur.execute(sql)
    result = cur.fetchone()[0]

    if result == 0:
        if content == None:
            sql = f"select subjectname from subjectlist where subindex={subject}"
            cur.execute(sql)
            result = cur.fetchone()[0]

            await ctx.send(f"{result}에 대한 내용 입력")
        elif len(content) >= 10 and len(content) <= 30:
            sql = f"select isprocess from subjectlist where subindex={subject}"
            cur.execute(sql)
            result = cur.fetchone()[0]

            print(result)

            if result == "Y":
                sql = f"select count(*) from postlist where subjectno={subject}"
                cur.execute(sql)
                postcount = cur.fetchone()[0]

                sql = f"insert into postlist(subjectno,postno,writer,content) values ({subject},{postcount+1},{ctx.author.id},'{content}')"
                print(sql)
                cur.execute(sql)
                sql = f"update userlist set point=point+1000"
                cur.execute(sql)
                await ctx.send("등록 완료 1000P지급")
            else:
                await ctx.send("토론이 끝난 주제입니다.")
        else:
            await ctx.send("글자수 10자 이상 30자 이하")
    else:
        await ctx.send("글쓰기 정지 상태입니다.")


@bot.command()
async def read(ctx, subject=None, postno=None):
    await ctx.send(get_post(subject, postno))


def get_post(subno, postno):
    url = f"http://127.0.0.1:8000/items?subjectno={subno}&postno={postno}"

    request = ul.Request(url)
    response = ul.urlopen(request)
    rescode = response.getcode()

    if rescode == 200:
        responsedata = response.read()
        print(responsedata)

        data = responsedata.decode("utf8").replace("<br>", "\n")

        return data

    return "fail"


@bot.command()
async def join(ctx):
    if CheckRegist(ctx.author.id) == 0:
        await ctx.send("가입을 해주세요")
        return

    sql = f"select level,lastdate from userlist where userid={ctx.author.id}"

    cur.execute(sql)
    result = cur.fetchone()

    level = result[0]
    last = result[1]

    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day

    index = 0
    temp1 = 0
    temp2 = 0

    while level > index:
        temp1 += 1000 * (index // 5 + 1)
        index += 5

    for i in range(level):
        temp2 += (i + 1) * 200

    temp3 = math.floor(0.2 * 1000 * (1.2 ** (level - 1)))

    todayp = temp1 + temp2 + temp3

    if last == int(f"{year}{month}{day}"):
        await ctx.send("이미 출첵함")
    else:
        sql = f"update userlist set point=point+{todayp}, lastdate={year}{month}{day}"
        cur.execute(sql)
        await ctx.send(f"{todayp}P 지급 완료")


def CheckPost(subjectno=None, postno=None):
    if subjectno == None:
        sql = "select subindex,subjectname from subjectlist where isprocess='Y'"

        reli = exesql(sql)

        sendtext = f"토론중인 주제 개수 : {len(reli)}개\n"

        for i in reli:
            sendtext += f"{i[0]} {i[1]}\n"

        result = sendtext
    else:
        sql = f"select subjectname from subjectlist where subindex={subjectno}"
        cur.execute(sql)
        subjectstr = cur.fetchone()[0]
        if postno == None:
            sql = f"select count(*) from postlist where subjectno={subjectno}"
            cur.execute(sql)
            result = f"{subjectstr}의 글 개수\n{cur.fetchone()[0]}개"
        else:

            sql = f"select content from postlist where subjectno={subjectno} and postno={postno}"
            cur.execute(sql)
            result = f"{subjectstr}의 {postno}번째 글\n" + cur.fetchone()[0]

    return result


def exesql(sql):
    cur.execute(sql)
    return cur.fetchall()


def givePoint(userid, point):
    sql = f"update userlist set point=point+{point} where userid={userid}"
    cur.execute(sql)


def CheckSubject(subno=None):

    sql = "select * from subjectlist"
    cur.execute()
    result = cur.fetchall()

    if subno == None:

        return len(result)

    if int(subno) > result:
        return False, "존재하지 않는 주제 번호"
    else:
        return True, result[int(subno) - 1][1]


@bot.command()
async def regist(ctx):
    result = CheckRegist(ctx.author.id)
    if result == 0:
        randstr = ""
        string_pool = string.ascii_letters + string.digits
        for i in range(20):
            randstr += random.choice(string_pool)
        sql = f"insert into userlist(userid,nickname) values ({ctx.author.id},'{randstr}')"
        cur.execute(sql)
        await ctx.send("가입 완료")
    else:
        await ctx.send("이미 가입되어있습니다.")


@bot.command()
async def levelup(ctx):
    # 가입 체크
    result = CheckRegist(ctx.author.id)
    if result == 0:
        await ctx.send("가입을 해주세요.")
        return

    # 레벨 체크
    sql = f"select level,point from userlist where userid={ctx.author.id}"

    cur.execute(sql)
    result = cur.fetchone()

    level = result[0]
    point = result[1]

    if level == 50:
        await ctx.send("만렙입니다.")
        return

    # 비용, 포인트 체크
    cost = math.floor(1000 * (1.2 ** (level - 1)))

    if point >= cost:
        # 포인트 차감
        sql = f"update userlist set point=point-{cost} where userid={ctx.author.id}"
        cur.execute(sql)

        success = 100
        # 확률 구하기
        for i in range(level):
            if (i + 1) % 10 == 9:
                success /= 2
            elif (i + 1) % 10 == 0:
                success = math.floor(success * 1.5) + 10
            else:
                success -= 2.3

        print((level, success))

        # 등업 시도
        dice = random.random() * 100

        # 성공시 렙업
        if dice < success:
            sql = f"update userlist set level=level+1 where userid={ctx.author.id}"
            cur.execute(sql)
            await ctx.send("성공")
        # 실패시 럭키팡 적립(비용의 30%)
        else:
            sql = f"update numstat set sum=sum+{math.floor(cost*0.3)} where name='stackluckypang'"
            cur.execute(sql)
            await ctx.send("레벨업에 실패하여 비용의 30% 럭키팡 적립")

    else:
        await ctx.send("포인트가 부족합니다.")
        return


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


# 정지 먹일때 필요한것
print(datetime.datetime.now().timestamp())
print((datetime.datetime.now() + datetime.timedelta(days=3)).timestamp())
bot.run(token)

from fastapi import FastAPI
from typing import Optional
import pymysql
import json
from fastapi.responses import HTMLResponse

app = FastAPI()

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


@app.get("/")
def read_root():
    return "hi discord board"


def exesql(sql):
    cur.execute(sql)
    return cur.fetchall()


@app.get("/all")
def read_item():
    sql = "select idx,subjectno,postno,content from postlist where status='show'"
    cur.execute(sql)
    result = cur.fetchall()
    print(result)

    senddata = ""

    index = 1

    for i in result:
        print(i)
        senddata += str(i)
        index += 1

    return senddata


@app.get("/items", response_class=HTMLResponse)
def read_item(subjectno: Optional[str] = None, postno: Optional[str] = None):
    try:
        print(type(postno))
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
            if postno == "None":
                sql = f"select idx,postno,content from postlist where subjectno={subjectno}"
                cur.execute(sql)
                res = cur.fetchall()
                result = ""
                for i in res:
                    result += f"{i}\n"
            else:

                sql = f"select content from postlist where subjectno={subjectno} and postno={postno}"
                cur.execute(sql)
                result = f"{subjectstr}의 {postno}번째 글\n" + cur.fetchone()[0]

        result = result.replace("\n", "<br>")

        return result
    except:
        return f"오류"

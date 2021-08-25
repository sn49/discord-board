import datetime
import os
import re


def write(subject, userid, content):

    count = 0
    for f in os.listdir("./data/"):
        if re.match(f"S\d{str(subject).zfill(3)}P\d{3}.disbo", f):
            count += 1

    postno = count + 1

    wfile = open(
        f"data/S{str(subject).zfill(3)}P{str(postno).zfill(3)}.disbo",
        "w",
        encoding="UTF-8",
    )

    ctime = datetime.datetime.now()
    year = ctime.year
    month = ctime.month
    day = ctime.day

    hour = ctime.hour
    minute = ctime.minute
    second = ctime.second

    writetext = f"{year}-{month}-{day}-{hour}-{minute}-{second}\n"
    writetext += f"{userid}\n"
    writetext += f"{content}\n\n동의 반대 리스트"

    wfile.write(writetext)

import math

level = 10

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

print(temp1)
print(temp2)
print(temp3)

print(todayp)

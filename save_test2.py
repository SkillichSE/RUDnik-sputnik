# save_test2.py
import json
def dataset_sat(number_sat):
    with open("data.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    tle_text=[]
    tle_num=0
    DO_NOT_OPEN=data
    line_1=line_2=""
    line_0=""
    #number_sat=(int(input("NUMBER: "))-1)*3
    for i in range(number_sat, number_sat+3):
        if tle_num==0:
            line_0=DO_NOT_OPEN[i]
        if tle_num==1:
            line_1=DO_NOT_OPEN[i]
        if tle_num==2:
            line_2=DO_NOT_OPEN[i]
        tle_text.append(DO_NOT_OPEN[i])
        #print(tle_text[tle_num])
        tle_num=tle_num+1
    return(line_0, line_1, line_2)
st=int(input("from: "))
en=int(input("to: "))+1
print("="*90)
for i in range(st, en, 1):
    line_0, line_1, line_2=dataset_sat(((i-1)*3))
    print("     ", line_0, "    ", i)
    print("     ", line_1)
    print("     ", line_2)
    print("="*90)


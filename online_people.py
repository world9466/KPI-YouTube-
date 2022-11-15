import pandas as pd
import pymysql,time,os
from datetime import datetime
from dateutil.relativedelta import relativedelta

time_start = time.time()
# 設定MySQL連線
db_settings = {
    "host": "ytdb1.ctitv.com.tw",
    "port": 3306,
    "user": "dbuser",
    "password": "66007766",
    "db": "dbLiveStreamListViewers",
    "charset": "utf8"
}
conn = pymysql.connect(**db_settings)

# 設定起始時間及持續月分，判斷輸入字數正確且字串僅由數字組成

while True:
    print('請輸入在線人數起算年份(ex.2021)：')
    date_year = input('請輸入在線人數起算年份(ex.2021)：')
    if len(date_year) == 4 and date_year.isdigit():
        print('請輸入在線人數起算月份(ex. 02 or 11)：')
        date_month = input('請輸入在線人數起算月份(ex. 02 or 11)：')
        while True:
            if len(date_month) == 2 and date_month.isdigit():
                break
            else:
                print('格式錯誤，請重新輸入2個數字的月份')
        break
    else:
        print('格式錯誤，請重新輸入4個數字的年份')

start = '{}-{}'.format(date_year,date_month)

while True:
    print('請輸入持續時間(單位:月份 , 預設輸入為 12 )：')
    duration = input('請輸入持續時間(單位:月份 , 預設輸入為 12 )：')
    if len(duration) < 3 and duration.isdigit():
        duration = int(duration)
        break
    else:
        print('輸入錯誤，請重新輸入')


# 建立月份LIST，先把start轉換為日期格式，然後找出往下數11個月的期間加到list
start = datetime.strptime(start, '%Y-%m')
month_list = []
for mon in range(duration):
    next_month = start + relativedelta(months=mon)
    month_list.append(next_month)

# 建立在線人數總表
online_people = {'節目':[],'在線人數_頂標':[],'在線人數_高標':[],'在線人數_中位數':[],'在線人數_低標':[]}
online_people = pd.DataFrame(online_people)

# 建立資料庫篩選條件
list_program = [
    ('中天電視','大直播','大直播'),
    ('中天新聞','中天午報','午間新聞'),
    ('正常發揮','正常發揮','正常發揮'),
    ('全球大視野','全球大視野','全球大視野'),
    ('大新聞大爆卦','大新聞大爆卦','大新聞大爆卦'),
    ('大新聞大爆卦','週末大爆卦','週末大爆卦'),
    ('頭條開講','頭條開講','頭條開講'),
    ('中天新聞','中天晚報','辣晚報'),
    ('全球大視野','前進戰略高地','前進戰略高地'),
    ('全球大視野','直球對決','國際直球對決')
    ]

###################################################################

# 先迭代節目表，然後在MySQL語法內迭代月份，抓取每個月的全部筆數，然後加總後做平均，列出數筆資料(視duration)
for program in list_program:

    channel = program[0]
    category = program[1]
    name = program[2]

    data_table = {'people':[]}
    data_table = pd.DataFrame(data_table)
    for month in month_list:
        with conn.cursor() as cursor:
            
            command = '''
            SELECT 觀看量 
            FROM ytLiveStreamListViewers 
            WHERE 資料時間 LIKE '{}%' AND 頻道名稱 = "{}" AND 影片類別 = "{}"
            '''.format(datetime.strftime(month,'%Y-%m'),channel,category) 

            # datetime.strftime 把整串時間轉換成只有年月

            # 下方為日期篩選用，有需要再加入，DAYOFWEEK 的 1 跟 7 分別代表周日跟周六
            '''
            AND TIME(資料時間) BETWEEN '23:00:00' AND '23:59:59'
            AND DAYOFWEEK(資料時間) NOT IN (1|7)
            '''
            
            cursor.execute(command)
            result = cursor.fetchall()
            count = len(result)
            total = 0
            # result 為tuple集合，迭代後相加
            for res in result:
                total+=res[0]
            if count == 0:
                avg = 0
            else:
                avg = round(total/count)
            
            avg_data = {'people':[avg]}
            avg_data = pd.DataFrame(avg_data)
            data_table = pd.concat([data_table,avg_data],ignore_index=True)


    views_max = data_table['people'].max()
    views_high = data_table['people'].quantile(q=0.75,interpolation='linear')
    views_med = data_table['people'].quantile(q=0.5,interpolation='linear')
    views_low = data_table['people'].quantile(q=0.25,interpolation='linear')

    table = {'節目':[name],'在線人數_頂標':[round(views_max)],'在線人數_高標':[round(views_high)],'在線人數_中位數':[round(views_med)],'在線人數_低標':[round(views_low)]}
    table = pd.DataFrame(table)
    online_people = pd.concat([online_people,table],ignore_index=True)
    print('節目：{}於資料庫撈取完成'.format(name))

###################################################################


print(online_people)
online_people.to_excel('../online_people.xlsx',encoding = 'utf-8-sig')

###################################################################
time_end = time.time()
print('資料庫撈取及計算及報表輸出共耗時',round(time_end - time_start,2),'秒')
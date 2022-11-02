import pandas as pd
import os,zipfile,re

####################################################

# 解壓縮檔案
def file_extract(channel):
    dirpath = '../channel/{}/壓縮檔'.format(channel)
    files = os.listdir(dirpath)
    for file in files:
        # 分配資料夾名稱
        if re.match('Date.*',file):
            folder_name = 'view_revenue_data'
        elif re.match('日期.*',file):
            folder_name = 'audience_data'

        # 把符合副檔名zip的壓縮檔都解壓縮
        if re.match('.*.zip',file):
            zf = zipfile.ZipFile('../channel/{}/壓縮檔/{}'.format(channel,file), 'r')
            zf.extractall(path = '../channel/{}/{}'.format(channel,folder_name))
    print('file extract success')

####################################################

# 讀取csv檔，輸出表格
def table_combine(channel):
    # 處理第一個表格
    table1 = pd.read_csv('../channel/{}/view_revenue_data/Table data.csv'.format(channel),encoding='utf8')
    table1 = table1.tail(-1)                                 # 不顯示總計
    table1 = table1.sort_values(['Date'],ascending=True)     # 用日期排列
    table1 = table1.reset_index()                            # 重設index
    table1.index = table1.index+1                            # 讓inedx從1開始

    # 處理第二個表格，整理成table3
    table2_folder_path = "../channel/{}/audience_data".format(channel)
    if os.path.isdir(table2_folder_path):
        table2 = pd.read_csv('../channel/{}/audience_data/表格資料.csv'.format(channel),encoding='utf8')
        table2 = table2.tail(-1)
        table2 = table2.sort_values(['日期'],ascending=True)
        table2 = table2.reset_index()
        table2.index = table2.index+1
        table3 = {'新訪客佔比':table2['新觀眾']/table1['Unique viewers']}
        table3 = pd.DataFrame(table3)
    else:
        print('create empty table')
        table3 = {'新訪客佔比':['NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN','NaN']}
        table3 = pd.DataFrame(table3)
        table3.index = table3.index+1


    # 選取所需欄位，建立新table
    table = {
        '日期':table1['Date'],
        '總觀看次數':table1['Views'],
        '總觀看時長(小時)':table1['Watch time (hours)'],
        '平均觀看時間比例':table1['Average percentage viewed (%)'],
        '不重複觀眾人數':table1['Unique viewers'],
        '新訪客佔比':table3['新訪客佔比'],
        '頻道營收(美金)':table1['Your estimated revenue (USD)']
        }
    table = pd.DataFrame(table)

    # 觀看次數取四分位數為指標
    views_max = table['總觀看次數'].max()
    views_high = round(table['總觀看次數'].quantile(q=0.75,interpolation='linear'))
    views_low = round(table['總觀看次數'].quantile(q=0.25,interpolation='linear'))
    
    # 觀看時長取四分位數為指標
    time_max = round(table['總觀看時長(小時)'].max())
    time_high = round(table['總觀看時長(小時)'].quantile(q=0.75,interpolation='linear'))
    time_low = round(table['總觀看時長(小時)'].quantile(q=0.25,interpolation='linear'))

    # 平均觀看時間比例取四分位數為指標
    dur_max = round(table['平均觀看時間比例'].max(),1)/100
    dur_high = round(table['平均觀看時間比例'].quantile(q=0.75,interpolation='linear'),1)/100
    dur_low = round(table['平均觀看時間比例'].quantile(q=0.25,interpolation='linear'),1)/100

    # 不重複觀眾人數
    uv_max = table['不重複觀眾人數'].max()
    uv_high = round(table['不重複觀眾人數'].quantile(q=0.75,interpolation='linear'))
    uv_low = round(table['不重複觀眾人數'].quantile(q=0.25,interpolation='linear'))

    # 新訪客佔比
    if  isinstance(table['新訪客佔比'][1], float):
        newaud_max = table['新訪客佔比'].max()
        newaud_high = table['新訪客佔比'].quantile(q=0.75,interpolation='linear')
        newaud_low = table['新訪客佔比'].quantile(q=0.25,interpolation='linear')
    elif  isinstance(table['新訪客佔比'][1], int):
        newaud_max = table['新訪客佔比'].max()
        newaud_high = table['新訪客佔比'].quantile(q=0.75,interpolation='linear')
        newaud_low = table['新訪客佔比'].quantile(q=0.25,interpolation='linear')
    else:
        newaud_max = 'NaN'
        newaud_high = 'NaN'
        newaud_low = 'NaN'

    #營收
    revenue_max = round(table['頻道營收(美金)'].max())
    revenue_high = round(table['頻道營收(美金)'].quantile(q=0.75,interpolation='linear'))
    revenue_low = round(table['頻道營收(美金)'].quantile(q=0.25,interpolation='linear'))

    # q 默認為0.5(中位數)，第一四分位數為0.25，第三四分位數為0.75
    # axis ： 0為index，1為columns (只能用在Dataframe)
    # numeric_only若為False，將計算日期時間和時間增量數據的分位數，跨謀(只能用在Dataframe)
    # interpolatoin 有5種 linear, lower, higher, midpoint, nearest
    # pos(position)算法為1+(n+1)*p ，p為分位數，n為總數
    # 若算出來不是整數，就用5個方法中的一個取值，默認 linear
    # linear: i + (j - i) * pos ，用pos值直接算
    # lower: i          選小的那個
    # higher: j         選大的那個
    # nearest: i or j   選最靠近的那個
    # midpoint: (i + j) / 2   相加除以2

    table_data = {
        '頻道':[channel],
        '總觀看次數_頂標':[views_max],'總觀看次數_高標':[views_high],'總觀看次數_低標':[views_low],
        '總觀看時長(小時)_頂標':[time_max],'總觀看時長(小時)_高標':[time_high],'總觀看時長(小時)_底標':[time_low],
        '平均觀看時間比例_頂標':[dur_max],'平均觀看時間比例_高標':[dur_high],'平均觀看時間比例_低標':[dur_low],
        '不重複觀眾人數_頂標':[uv_max],'不重複觀眾人數_高標':[uv_high],'不重複觀眾人數_低標':[uv_low],
        '新訪客佔比_頂標':[newaud_max],'新訪客佔比_高標':[newaud_high],'新訪客佔比_低標':[newaud_low],
        '頻道營收(美金)_頂標':[revenue_max],'頻道營收(美金)_高標':[revenue_high],'頻道營收(美金)_低標':[revenue_low]
        }
    table_data = pd.DataFrame(table_data)
    global KPI_table
    KPI_table = pd.concat([KPI_table,table_data],ignore_index=True)



####################################################

channel = ['中天電視','中天新聞','大新聞大爆卦','正常發揮','頭條開講','全球大視野',
'2022全台選舉大PK','論文門開箱','健康我+1','我愛貓大','康熙好經典','中天娛樂頻道','毛球烏托邦',
'台灣大搜索','來去check IN','姐的星球','吃瓜第一排','我愛小明星大跟班','同學來了']


KPI_table = {
    '頻道':[],    
    '總觀看次數_頂標':[],'總觀看次數_高標':[],'總觀看次數_低標':[],
    '總觀看時長(小時)_頂標':[],'總觀看時長(小時)_高標':[],'總觀看時長(小時)_底標':[],
    '平均觀看時間比例_頂標':[],'平均觀看時間比例_高標':[],'平均觀看時間比例_低標':[],
    '不重複觀眾人數_頂標':[],'不重複觀眾人數_高標':[],'不重複觀眾人數_低標':[],
    '新訪客佔比_頂標':[],'新訪客佔比_高標':[],'新訪客佔比_低標':[],
    '頻道營收(美金)_頂標':[],'頻道營收(美金)_高標':[],'頻道營收(美金)_低標':[]
    }
KPI_table = pd.DataFrame(KPI_table)


for ch in channel:
    file_extract(ch)
    table_combine(ch)
KPI_table.to_csv('../channel_KPI.csv',encoding='utf-8-sig')

print(KPI_table)
import pandas as pd
import os,zipfile,re

####################################################

# 解壓縮檔案
def file_extract(program):
    dirpath = '../program/{}/壓縮檔'.format(program)
    files = os.listdir(dirpath)
    for file in files:
        # 建立資料夾名稱，取出壓縮檔名字內的數字，其他都去除
        folder_name = re.findall('\(.*\)',file)
        folder_name = folder_name[0]               
        folder_name = re.sub('[\(\)]','',folder_name)

        # 把符合副檔名zip的壓縮檔都解壓縮
        if re.match('.*.zip',file):
            zf = zipfile.ZipFile('../program/{}/壓縮檔/{}'.format(program,file), 'r')
            zf.extractall(path = '../program/{}/{}'.format(program,folder_name))
    print('file extract success')

####################################################

# 計算各表格總值，合併到 KPI_table
def table_combine(program):
    # 先將各影片group的值合併，每500部影片會有一個資料夾，每個節目的資料夾總數不同
    # 資料夾命名從0到50，迭代讀取只要資料夾內有Table data.csv檔案就進行讀取
    # 要最先迭代月份，順序是先讀取完每個資料夾的單月去做總計，然後就能依序做出每個月的統計

    views_count = 0
    watchtime_count = 0
    duration_count = 0
    revenue_count = 0
    table = {'總觀看次數':[],'總觀看時長(小時)':[],'平均觀看比例':[],'頻道營收(美金)':[]}
    table = pd.DataFrame(table)

    for month in ['-01','-02','-03','-04','-05','-06','-07','-08','-09','-10','-11','-12']:
        views_count = 0
        watchtime_count = 0
        duration_count = 0
        revenue_count = 0
        # 以數字命名的資料夾內的Table data.csv若存在就進行讀取
        count_file = 0
        for num in range(50):
            num = str(num)
            folder_path = '../program/{}/{}/Table data.csv'.format(program,num)
            if os.path.isfile(folder_path):
                count_file+=1
                table_origin = pd.read_csv('../program/{}/{}/Table data.csv'.format(program,num),encoding = 'utf8')

                # 觀看數加總
                views = table_origin['Views'][table_origin['Date'].str.contains(month)]            
                for value in views.values:
                    views_count+=value
                # 觀看時長加總
                watchtime = table_origin['Watch time (hours)'][table_origin['Date'].str.contains(month)]            
                for value in watchtime.values:
                    watchtime_count+=value
                # 觀看比例平均(字串取出時分秒，再化成秒數總計)
                duration = table_origin['Average percentage viewed (%)'][table_origin['Date'].str.contains(month)]            
                for value in duration.values:
                    duration_count+=value
                # 營收加總
                revenue = table_origin['Your estimated revenue (USD)'][table_origin['Date'].str.contains(month)]            
                for value in revenue.values:
                    revenue_count+=value
        # 整理出每月的數據生成一筆資料
        table_data = {
            '總觀看次數':[views_count],'總觀看時長(小時)':[round(watchtime_count)],
            '平均觀看比例':[round(duration_count/count_file,1)],'頻道營收(美金)':[round(revenue_count)]}
        table_data = pd.DataFrame(table_data)
        # 把這筆資料新增到 table
        table = pd.concat([table,table_data],ignore_index = True)
    table.index = table.index+1
    
    #print(table)
    # 觀看次數取四分位數為指標，有的月份頻道還沒上線
    views_max = table['總觀看次數'][table['總觀看次數'] != 0 ].max()
    views_high = round(table['總觀看次數'][table['總觀看次數'] != 0 ].quantile(q=0.75,interpolation='linear'))
    views_med = round(table['總觀看次數'][table['總觀看次數'] != 0 ].quantile(q=0.5,interpolation='linear'))
    views_low = round(table['總觀看次數'][table['總觀看次數'] != 0 ].quantile(q=0.25,interpolation='linear'))
    
    # 觀看時長取四分位數為指標
    time_max = round(table['總觀看時長(小時)'][table['總觀看時長(小時)'] != 0 ].max())
    time_high = round(table['總觀看時長(小時)'][table['總觀看時長(小時)'] != 0 ].quantile(q=0.75,interpolation='linear'))
    time_med = round(table['總觀看時長(小時)'][table['總觀看時長(小時)'] != 0 ].quantile(q=0.5,interpolation='linear'))
    time_low = round(table['總觀看時長(小時)'][table['總觀看時長(小時)'] != 0 ].quantile(q=0.25,interpolation='linear'))

    # 平均觀看比例取四分位數為指標
    dur_max = round(table['平均觀看比例'][table['平均觀看比例'] != 0 ].max(),1)/100
    dur_high = round(table['平均觀看比例'][table['平均觀看比例'] != 0 ].quantile(q=0.75,interpolation='linear'),1)/100
    dur_med = round(table['平均觀看比例'][table['平均觀看比例'] != 0 ].quantile(q=0.5,interpolation='linear'),1)/100
    dur_low = round(table['平均觀看比例'][table['平均觀看比例'] != 0 ].quantile(q=0.25,interpolation='linear'),1)/100

    #營收
    revenue_max = round(table['頻道營收(美金)'][table['頻道營收(美金)'] != 0 ].max())
    revenue_high = round(table['頻道營收(美金)'][table['頻道營收(美金)'] != 0 ].quantile(q=0.75,interpolation='linear'))
    revenue_med = round(table['頻道營收(美金)'][table['頻道營收(美金)'] != 0 ].quantile(q=0.5,interpolation='linear'))
    revenue_low = round(table['頻道營收(美金)'][table['頻道營收(美金)'] != 0 ].quantile(q=0.25,interpolation='linear'))

    table_data_2 = {
        '節目':[program],    
        '總觀看次數_頂標':[views_max],'總觀看次數_高標':[views_high],'總觀看次數_中位數':[views_med],'總觀看次數_低標':[views_low],
        '總觀看時長(小時)_頂標':[time_max],'總觀看時長(小時)_高標':[time_high],'總觀看時長(小時)_中位數':[time_med],'總觀看時長(小時)_底標':[time_low],
        '平均觀看比例_頂標':[dur_max],'平均觀看比例_高標':[dur_high],'平均觀看比例_中位數':[dur_med],'平均觀看比例_低標':[dur_low],
        '頻道營收(美金)_頂標':[revenue_max],'頻道營收(美金)_高標':[revenue_high],'頻道營收(美金)_中位數':[revenue_med],'頻道營收(美金)_低標':[revenue_low],
        }
    table_data_2 = pd.DataFrame(table_data_2)
    global KPI_table
    KPI_table = pd.concat([KPI_table,table_data_2],ignore_index=True)

####################################################

KPI_table = {
    '節目':[],    
    '總觀看次數_頂標':[],'總觀看次數_高標':[],'總觀看次數_中位數':[],'總觀看次數_低標':[],
    '總觀看時長(小時)_頂標':[],'總觀看時長(小時)_高標':[],'總觀看時長(小時)_中位數':[],'總觀看時長(小時)_底標':[],
    '平均觀看比例_頂標':[],'平均觀看比例_高標':[],'平均觀看比例_中位數':[],'平均觀看比例_低標':[],
    '頻道營收(美金)_頂標':[],'頻道營收(美金)_高標':[],'頻道營收(美金)_中位數':[],'頻道營收(美金)_低標':[],
    }
KPI_table = pd.DataFrame(KPI_table)


program_list = ['大新聞大爆卦','週末大爆卦','頭條開講','辣晚報','前進戰略高地','國際直球對決',
'論文門開箱','熱搜發燒榜','頭條點新聞','世界越來越盧','鄭妹看世界','真心話大冒險','螃蟹秀開鍘',
'琴謙天下事','新聞千里馬','洪流洞見','小麥的健康筆記','詩瑋愛健康','金牌特派','阿比妹妹',
'食安趨勢報告','民間特偵組','全球政經周報','中天車享家','老Z調查線','詭案橞客室','靈異錯別字',
'宏色禁區','獸身男女','窩星球','愛吃星球','流行星球','小豪出任務','政治新人榜','綠也掀桌','你的豪朋友']
for program in program_list:
    file_extract(program)
    table_combine(program)

print(KPI_table)

KPI_table.to_excel('../program_KPI.xlsx',encoding = 'utf-8-sig')
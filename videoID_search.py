import pandas as pd
import re,time


start = time.time()
##################################################################################

# 讀取影片報表CSV檔
video_data = pd.read_csv('../video_report_ctitv_V_v1-3.csv',encoding = 'utf8')

# 去掉VIDEO ID的兩邊空白避免篩選錯誤
video_data['video_id'].str.strip()

# 照日期排序
video_data = video_data.sort_values('time_published',ascending=True)



##################################################################################

# 取出大新聞大爆卦的資料
video_bignews_id = video_data[['video_id','time_published']][video_data['video_title'].str.contains('【大新聞大爆卦.*?')]

# 建立新表格，把搜尋出的資料貼上去(重置index用)
bignews_table = {'影片ID(平日爆卦)':[],'發布時間(平日爆卦)':[]}
bignews_table = pd.DataFrame(bignews_table)

# 沒有發布的影片，發布時間會是空白，有發布時間的資料都會是20開頭，只取有發布的影片
for video in video_bignews_id.values:
    if re.match('20.*',str(video[1])):
        table = {'影片ID(平日爆卦)':[video[0]],'發布時間(平日爆卦)':[video[1]]}
        table = pd.DataFrame(table)
        bignews_table = pd.concat([bignews_table,table],ignore_index=True)

# 加入影片數量欄位
mount_table = {'影片數':[len(bignews_table['影片ID(平日爆卦)'])]}
mount_table = pd.DataFrame(mount_table)
bignews_table = bignews_table.join(mount_table,how = 'outer',rsuffix = 'x')
bignews_table.index = bignews_table.index+1

##################################################################################

# 取出週末大爆卦的資料
video_weekend_id = video_data[['video_id','time_published']][video_data['video_title'].str.contains('【週末大爆卦.*?')]

weekend_table = {'影片ID(週末爆卦)':[],'發布時間(週末爆卦)':[]}
weekend_table = pd.DataFrame(weekend_table)

for video in video_weekend_id.values:
    if re.match('20.*',str(video[1])):
        table = {'影片ID(週末爆卦)':[video[0]],'發布時間(週末爆卦)':[video[1]]}
        table = pd.DataFrame(table)
        weekend_table = pd.concat([weekend_table,table],ignore_index=True)

# 加入影片數量欄位
mount_table = {'影片數':[len(weekend_table['影片ID(週末爆卦)'])]}
mount_table = pd.DataFrame(mount_table)
weekend_table = weekend_table.join(mount_table,how = 'outer',rsuffix = 'x')
weekend_table.index = weekend_table.index+1

##################################################################################

# 取出頭條開講的資料，str.contains使用 | 符號可以選取多個關鍵字
video_headline_id = video_data[['video_id','time_published']][video_data['video_title'].str.contains('【頭條開講.*?|專家來開講.*?')]

headline_table = {'影片ID(頭條開講)':[],'發布時間(頭條開講)':[]}
headline_table = pd.DataFrame(headline_table)

for video in video_headline_id.values:
    if re.match('20.*',str(video[1])):
        table = {'影片ID(頭條開講)':[video[0]],'發布時間(頭條開講)':[video[1]]}
        table = pd.DataFrame(table)
        headline_table = pd.concat([headline_table,table],ignore_index=True)

# 加入影片數量欄位
mount_table = {'影片數':[len(headline_table['影片ID(頭條開講)'])]}
mount_table = pd.DataFrame(mount_table)
headline_table = headline_table.join(mount_table,how = 'outer',rsuffix = 'x')
headline_table.index = headline_table.index+1

##################################################################################


program_lsit = ['辣晚報','前進戰略高地','國際直球對決','論文門開箱','熱搜發燒榜','頭條點新聞',
'世界越來越盧','鄭妹看世界','真心話大冒險','螃蟹秀開鍘','琴謙天下事','新聞千里馬','洪流洞見',
'小麥的健康筆記','詩瑋愛健康','金牌特派','阿比妹妹','食安趨勢報告','民間特偵組','全球政經周報',
'中天車享家','老Z調查線','詭案橞客室','靈異錯別字','宏色禁區','獸身男女','窩星球','愛吃星球',
'流行星球','小豪出任務','政治新人榜','綠也掀桌','你的豪朋友']

# 使用關鍵字搜尋節目
def video_id_search(program):
    video_data_id = video_data[['video_id','time_published']][video_data['video_title'].str.contains('.*?{}.*?'.format(program))]

    data_table = {'影片ID({})'.format(program):[],'發布時間({})'.format(program):[]}
    data_table = pd.DataFrame(data_table)

    for video in video_data_id.values:
        if re.match('20.*',str(video[1])):
            table = {'影片ID({})'.format(program):[video[0]],'發布時間({})'.format(program):[video[1]]}
            table = pd.DataFrame(table)
            data_table = pd.concat([data_table,table],ignore_index=True)

    # 加入影片數量欄位
    mount_table = {'影片數({})'.format(program):[len(data_table['影片ID({})'.format(program)])]}
    mount_table = pd.DataFrame(mount_table)
    data_table = data_table.join(mount_table,how = 'outer',rsuffix = 'x')
    data_table.index = data_table.index+1
    global id_table
    id_table = id_table.join(data_table,how = 'outer',rsuffix = 'xx')
    print('節目：<{}>的影片ID搜尋完成'.format(program))


##################################################################################

id_table = bignews_table.join(weekend_table,how = 'outer',rsuffix = 'x')
id_table = id_table.join(headline_table,how = 'outer',rsuffix = 'xx')

# 搜尋每個節目，把表格合併到 id_table
for program in program_lsit:
    video_id_search(program)

# 輸出excel檔
id_table.to_excel('../allvideo_id.xlsx',encoding = 'utf-8-sig')


print('===============  video_id_search successful  ===============')
end = time.time()
print('資料計算及報表輸出共耗時',round(end - start,2),'秒')
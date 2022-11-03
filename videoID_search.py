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

# 建立節目清單， .*? 是用在str.contains()的判別上
program_lsit = ['【大新聞大爆卦.*?','【週末大爆卦.*?','【頭條開講.*?|專家來開講.*?',
'.*?辣晚報.*?','.*?前進戰略高地.*?','.*?國際直球對決.*?','.*?論文門開箱.*?',
'.*?熱搜發燒榜.*?','.*?頭條點新聞.*?','.*?世界越來越盧.*?','.*?鄭妹看世界.*?',
'.*?真心話大冒險.*?','.*?螃蟹秀開鍘.*?','.*?琴謙天下事.*?','.*?新聞千里馬.*?',
'.*?洪流洞見.*?','.*?小麥的健康筆記.*?','.*?詩瑋愛健康.*?','.*?金牌特派.*?',
'.*?阿比妹妹.*?','.*?食安趨勢報告.*?','.*?民間特偵組.*?','.*?全球政經周報.*?',
'.*?中天車享家.*?','.*?老Z調查線.*?','.*?詭案橞客室.*?',
'.*?靈異錯別字.*?|.*?鬼錯字.*?','.*?宏色禁區.*?|.*?宏色封鎖線.*?','.*?獸身男女.*?',
'.*?窩星球.*?','.*?愛吃星球.*?','.*?流行星球.*?','.*?小豪出任務.*?',
'.*?政治新人榜.*?','.*?綠也掀桌.*?','.*?你的豪朋友.*?']

# 使用關鍵字搜尋節目
def video_id_search(program):
    video_data_id = video_data[['video_id','time_published']][video_data['video_title'].str.contains('{}'.format(program))]

    # 把正則用的.*?去掉，把多餘的字移除
    if '大新聞大爆卦' in program:
        program = '平日爆卦'
    elif '週末大爆卦' in program:
        program = '週末爆卦'
    elif '頭條開講' in program:
        program = '頭條開講'
    elif '靈異錯別字' in program:
        program = '靈異錯別字'
    elif '宏色禁區' in program:
        program = '宏色禁區'
    else:
        program = re.sub('[.\*\?]','',program)

    # 建立新表格，把搜尋出的資料貼上去(重置index用)
    data_table = {'影片ID({})'.format(program):[],'發布時間({})'.format(program):[]}
    data_table = pd.DataFrame(data_table)

    # 沒有發布的影片，發布時間會是空白，有發布時間的資料都會是20開頭，只取有發布的影片
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

id_table = pd.DataFrame()


# 搜尋每個節目，把表格合併到 id_table
for program in program_lsit:
    video_id_search(program)

# 輸出excel檔
id_table.to_excel('../allvideo_id.xlsx',encoding = 'utf-8-sig')


print('===============  video_id_search successful  ===============')
end = time.time()
print('資料計算及報表輸出共耗時',round(end - start,2),'秒')
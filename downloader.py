from bs4 import BeautifulSoup as bs
import shutil
import requests

init_url ='https://irs.thsrc.com.tw/IMINT/'

class Session(requests.Session):
    def request(self, *args, **kwargs):
        return super().request(
            headers=self.headers,
            cookies=self.cookies,
            *args, **kwargs
        )

def start_session():
    fake_session = Session()
    fake_session.headers.update(
        {
            "User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        }
    )
    return fake_session

def get_s1_component(referer,content):
    soup = bs(content,'html.parser')
    a_tags = soup.find_all('a')
    img_tags = soup.find_all('img')
    form_tags = soup.find_all('form')
    for a_tag in a_tags:
        text = a_tag.text
        while ' ' in text :
            text = text.replace(' ','')
        while '\n' in text:
            text = text.replace('\n','')
        while '\t' in text:
            text = text.replace('\t','')
        while '\r' in text:
            text = text.replace('\r','')
        if text == '語音播放':
            voice_tag = a_tag

    for img_tag in img_tags:
        img_tag_id = img_tag.get('id')
        if img_tag_id == 'BookingS1Form_homeCaptcha_passCode':
            code_tag = img_tag

            #print(code_tag)

    for form_tag in form_tags:
        form_tag_id = form_tag.get('id')
        if form_tag_id == 'BookingS1Form':
            form_tag_url = referer + form_tag['action']

            #print(code_tag)

    voice_tag_url = referer + voice_tag['href']
    code_tag_url = referer + code_tag['src']

    return (voice_tag_url,code_tag_url,form_tag_url)

def get_s2_component(referer,content):
    soup = bs(content,'html.parser')
    form_tags = soup.find_all('form')
    input_tags = soup.find_all('input')
    value_list = []
    for form_tag in form_tags:
        form_tag_id = form_tag.get('id')
        if form_tag_id == 'BookingS2Form':
            form_tag_url = referer + form_tag['action']
    
    for input_tag in input_tags:
        try:
            input_tag_value = input_tag['value']
            if input_tag_value.startswith('radio'):
                value_list.append(input_tag)
        except KeyError:
            pass

    return form_tag_url, value_list

def get_voice(session, url):
    r = session.get(url, stream=True)
    if r.status_code == 200:
        with open('voice.wav', 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)  

def get_code(session, url):
    r = session.get(url, stream=True)
    if r.status_code == 200:
        with open('code.png', 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)     

def get_s1_post_form(code):
    return {
        'BookingS1Form:hf:0': None,  #這個不要動
        'selectStartStation': 7, #起始站，每個站都有不同的編號
        'selectDestinationStation': 2, #抵達站，每個站都有不同的編號
        'trainCon:trainRadioGroup': 0,
        'bookingMethod': 0,
        'toTimeInputField': '2019/12/26',  #去程票時間
        'toTimeTable': '200P',   # 他Timetable的規律我還沒去看
        'toTrainIDInputField': None,
        #'backTimeCheckBox': 'on', # 如果要訂回程票 這個要on
        'backTimeInputField': '2019/12/26', #回程票時間
        'backTimeTable': '1130P', 
        'backTrainIDInputField': None,
        'ticketPanel:rows:0:ticketAmount': '1F', # F H W E P 分別有代表不同的族群，分別是成人票.... 其他我忘了
        'ticketPanel:rows:1:ticketAmount': '0H',
        'ticketPanel:rows:2:ticketAmount': '0W',
        'ticketPanel:rows:3:ticketAmount': '0E',
        'ticketPanel:rows:4:ticketAmount': '0P',
        'homeCaptcha:securityCode': code,
        'SubmitButton': '開始查詢',
    }

def get_s2_post_form(radio):
    return {
        'BookingS2Form:hf:0': None,
        "TrainQueryDataViewPanel:TrainGroup": radio,  #車次表
        "SubmitButton": "確認車次"
    }

def post_test(session,url,r_url,form):
    print('target: ',url)
    print('referer: ',r_url)
    print('data: ', form)
    session.headers.update({
        "Referer":r_url
    })
    resp = session.post(url,data=form)
    
    return session.post(url,data=form)

if __name__ == "__main__":
    s = start_session() # session就把他先想像成瀏覽器開啟就好
    r = s.get(init_url) # init_url是主頁面網址
    v,c,f = get_s1_component(init_url,r.text)  #這個function是用來取得訂票第一個步驟所需要的原件
    get_code(s, c) # 取得 驗證碼圖片
    get_voice(s, v) # 取得 語音 
    code = input('code: ') # 這裡可以把它取代成用 演算法 得出來的驗證碼字串
    form = get_s1_post_form(code) # 這個是取得通過第一階段的表單 詳細你可以去看 get_s1_post_form，裡面照理說要依照每個人調整參數，例如你可能要訂的是2020/01/11的票
    rp = post_test(s, f, r.url, form) # 這個是把上面拿到的表單上傳
    print('after s1: ',rp.url) 
    f_u,v = get_s2_component(rp.url, rp.text)
    #print(rp.text)
    #print(f)
    print('target radio:', v[0]['value'])
    form = get_s2_post_form(v[0]['value'])
    rpp = post_test(s, f_u, rp.url, form)
    print('after s2: ',rpp.url)
    with open('test.html','w',encoding='utf-8') as f: #這兩行是我用來抓HTML下來用檔案分析的 但我現在只有破解到第二階段 我明天要考大洞 QQ
        f.write(rpp.text) #這兩行是我用來抓HTML下來用檔案分析的 但我現在只有破解到第二階段 我明天要考大洞 QQ
    
"""
BookingS1Form:hf:0: 
selectStartStation: 2
selectDestinationStation: 6
trainCon:trainRadioGroup: 0
bookingMethod: 0
toTimeInputField: 2019/12/17
toTimeTable: 1200N
toTrainIDInputField: 
backTimeCheckBox: on
backTimeInputField: 2019/12/17
backTimeTable: 1100P
backTrainIDInputField: 
ticketPanel:rows:0:ticketAmount: 1F
ticketPanel:rows:1:ticketAmount: 0H
ticketPanel:rows:2:ticketAmount: 0W
ticketPanel:rows:3:ticketAmount: 0E
ticketPanel:rows:4:ticketAmount: 0P
homeCaptcha:securityCode: RFQQ
SubmitButton: 開始查詢
"""

"""
BookingS2Form:hf:0: 
TrainQueryDataViewPanel:TrainGroup: radio18
SubmitButton: 確認車次
"""
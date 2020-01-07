from selenium import webdriver as w
from downloader import *
import requests
import time

#init_url ='https://irs.thsrc.com.tw/IMINT/'

#option = w.ChromeOptions()
#option.add_experimental_option('excludeSwitches', ['enable-automation'])

#driver = w.Chrome(options=option)
#driver.get(init_url)

#confirm_xpath='//*[@id="btn-confirm"]'
#confirms = driver.find_elements_by_xpath(confirm_xpath)
#confirms[0].click()

#time.sleep(.3)
# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36
#source_content = driver.page_source
#cookies = driver.get_cookies()
#user_agent = driver.execute_script("return navigator.userAgent;")
#current_url = driver.current_url

#pickle.dump(cookies, open("cookies.pkl", "wb"))
#cookies = pickle.load(open("cookies.pkl", "rb"))

#fake_session = requests.session()
#fake_session.headers.update(
#    {"User-Agent":user_agent,"Referer":init_url}
#)

#for cookie in cookies:
#    fake_session.cookies.set(cookie['name'], cookie['value'])

#v, c = get_component(current_url,source_content)

#get_voice(fake_session, v)
#get_code(fake_session, c)
#print(v)
#print(c)

if __name__ == "__main__":
    option = w.ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    driver = w.Chrome(options=option)
    driver.get('https://www.google.com')

    s = start_session()
    r = s.get(init_url)
    v,c,f = get_s1_component(init_url,r.text)
    get_code(s, c)
    get_voice(s, v)
    code = input('code: ')
    form = get_s1_post_form(code)
    rp = post_test(s, f, r.url, form)
    print('after s1: ',rp.url)
    f_u,v = get_s2_component(rp.url, rp.text)
    #print(rp.text)
    #print(f)
    print('target radio:', v[0]['value'])
    form = get_s2_post_form(v[0]['value'])
    rpp = post_test(s, f_u, rp.url, form)
    print('after s2: ',rpp.url)
    
    for c in s.cookies :
        driver.add_cookie({'name': c.name, 'value': c.value, 'path': c.path, 'expiry': c.expires})
    driver.header_overrides = {
        'Referer': init_url,
    }
    driver.get(rp.url)
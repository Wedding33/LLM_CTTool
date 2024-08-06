# 替换下列示例中的API Key与Secret Key
import requests
import json


def get_access_token():
        
    url = "https://aip.baidubce.com/oauth/2.0/token?client_id=M5F174kw8gQ8GOEkAGEgEJpl&client_secret=j5TyE1MrykRIpCkk4WcuNndhf4dDMifa&grant_type=client_credentials"
    
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    return response.json().get("access_token")
    
def main():
     
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/yi_34b_chat?access_token=" + get_access_token()
    
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": "推荐一些中国自驾游路线"
            }
        ],
         "stream": True
    })
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload, stream=True)
    
    for line in response.iter_lines():
        print(line.decode("UTF-8"))
    

if __name__ == '__main__':
    main()

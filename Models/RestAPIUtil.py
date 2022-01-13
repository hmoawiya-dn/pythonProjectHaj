import json
import requests

class RestAPIUtil:
    def postAPIrequest(url,data,authorizationToken=''):
        headers={"content-type": "application/json", 'Authorization': authorizationToken}
        print(f"sending request {data} to {url}")
        response = requests.post(url, json=data, headers=headers, verify=False)
        print(f'Status code of the request={int(response.status_code)}')
        data = json.loads(response.text)
        print(f'Response of the request ={data}')
        assert (response.status_code==200)
        return data

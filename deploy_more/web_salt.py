import requests
import json
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
import ssl
# 禁用安全请求警告
disable_warnings(InsecureRequestWarning)


ssl._create_default_https_context = ssl._create_unverified_context#设置ssl不认证,貌似不好使，直接requests参数设置不认证

class web_salt_api:
    def __init__(self,host,port,username,password):
        self.__host=host
        self.__port=port
        self.__username=username
        self.__password=password
        self.__token=''
        self.__eauth='pam'
        self.__url='https://{0}:{1}'.format(host,port)



    def request_post(self,in_url,params,):
        try:
            url = self.__url + in_url
            response=requests.post(url,params,headers=self.get_header(),verify=False)#最后一个参数为跳过ssl证书验证
            return response.text,None#第二个返回值控制报错内容的返回
        except Exception as e:
            return None,str(e)

    def login(self):
        if self.__token:
            return 2
        params={'username':self.__username,'password':self.__password,'eauth':self.__eauth}
        response,err=self.request_post('/login',params)
        if not response:
            #print('POST ERROR : '+err)
            return 0
        jl = json.loads(response)
        self.__token = jl['return'][0]['token']
        return 1

    def test(self):
        params={'client':'local','tgt':'*','fun':'test.ping'}
        response,err=self.request_post('/',params)
        if not response:
            return 0
        return response

    def get_header(self):
       return {'X-Auth-Token': self.__token, 'Accept': 'application/json'} #head基本一致

    def get_minions(self):
        ret_keys={}
        params={'client':'wheel','fun':'key.list_all'}
        response,err =self.request_post('/',params)
        if response:
            ret_keys=json.loads(response)["return"][0]['data']['return']
        return ret_keys

    def get_minions_pre(self):
        if 'minions_pre' in self.get_minions() :

            return self.get_minions()['minions_pre']
        return {}

    def get_minions_acc(self):
        if 'minions' in self.get_minions() :
            return self.get_minions()['minions']
        return {}

if __name__ == '__main__':
    wsa=web_salt_api('192.168.29.129','8080','saltapi','password')
    wsa.login()
    print(wsa.test())
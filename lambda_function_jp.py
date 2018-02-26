import json
import os
import time
import datetime
import uuid
from io import StringIO
import requests
import boto3

bucket_name = os.environ['bucket_name']
group = os.environ['group']
base_url = os.environ['base_url']

def read_s3():
    s3 = boto3.resource('s3')
    content_object = s3.Object('aruba-central', 'central_token.json')
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    return json_content

#### Upload Json to S3 ####
def upload_s3(text,key):
    s3 = boto3.client('s3')
    handler = StringIO(text)
    s3.put_object(
        Bucket = bucket_name,
        Key = key,
        Body = handler.read(),
        ContentType = 'application/json; charset=utf-8'
    )

#### Refresh_API_Token ####
def refresh_token(token_dict):
    client_id = token_dict['client_id']
    client_secret = token_dict['client_secret']
    refresh_token = token_dict['refresh_token']
    url = base_url+"oauth2/token?client_id="+client_id+"&client_secret="+client_secret+"&refresh_token="+refresh_token+"&grant_type=refresh_token"

    response = requests.request("POST", url)
    token_dict['refresh_token'] = response.json()['refresh_token']
    token_dict['access_token'] = response.json()['access_token']
    access_token = response.json()['access_token']
    text = json.dumps(token_dict)
    upload_s3(text,"central_token.json")
    return access_token


#### AP Status ####
def get_ap_status(access_token):
    ap_status = []
    url = base_url+"monitoring/v1/aps?access_token="+access_token+"&group="+group+"&status=Up"
    s = requests.session()
    r = s.request("GET", url)
    ap_status = [{"up_count": r.json()['count']}]

    url = base_url+"monitoring/v1/aps?access_token="+access_token+"&group="+group+"&status=Down"
    s = requests.session()
    r = s.request("GET", url)
    ap_status.append({"down_count":r.json()['count']})

    return (ap_status)

#### Get Total Clients ####
def get_total_client(access_token):
    url = base_url+"monitoring/v1/clients/count?access_token="+access_token+"&group="+group
    s = requests.session()
    r = s.request("GET", url)
    count = r.json()['count'] - 1
    client = r.json()['samples'][count]['client_count']   
    return (client)

#### Get Application List ####
def get_application(access_token):
    url = base_url+"apprf/v1/applications?access_token="+access_token+"&group="+group
    s = requests.session()
    r = s.request("GET", url)
    application = []
    application = [{"number" : 1,  "name" : r.json()['result'][0]['name'],"percent" : r.json()['result'][0]['percent_usage']}]
    for i in range(4):
        application.append({"number" : i+2, "name" : r.json()['result'][i+1]['name'],"percent" : r.json()['result'][i+1]['percent_usage']})
    return (application)


#### Top Client ####
def get_top_client(access_token):
    url = base_url+"monitoring/v1/clients/bandwidth_usage/topn?access_token="+access_token+"&group="+group
    s = requests.session()
    r = s.request("GET", url)
    top_client = [{"name":r.json()['clients'][0]['name'],"rx_bytes":r.json()['clients'][0]['rx_data_bytes'],"tx_bytes":r.json()['clients'][0]['tx_data_bytes']}]  
    return (top_client)

#### Get Firmware Version ####
def get_firmware(access_token):
    url = base_url +"firmware/v1/swarms?access_token="+access_token+"&group="+group
    s = requests.session()
    r = s.request("GET", url)
    firmware = [{"current_version" : r.json()['swarms'][0]['firmware_version']}]
    firmware.append ({"recommended_version" : r.json()['swarms'][0]['recommended']})
    return (firmware)



#### Create Message ####
def create_message(ap_status,firmware,total_client,application,top_client):
    message = []
    jst = datetime.datetime.now() + datetime.timedelta(hours=9)
    text = jst.strftime("%Y年%m月%d日%H時%M分頃の情報です")   
#    text = time.strftime("%Y年%m月%d日%H時%M分頃の情報です", time.gmtime())
    message.append({
		"uid": str(uuid.uuid4()),
		"updateDate": time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime()),
        "titleText":text, 
        "mainText": text
    })


    up_count = ap_status[0]['up_count']
    down_count = ap_status[1]['down_count']
    text = "{}台のAPが稼働中、{}台のAPがダウンしています".format(up_count,down_count)
    message.append({
		"uid": str(uuid.uuid4()),
		"updateDate": time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime()),
        "titleText":text, 
        "mainText": text
    })
    
    current = firmware[0]['current_version']
    recommended = firmware[1]['recommended_version']
    text = "現在のファームウェアバージョンは{}、推奨バージョンは{}です".format(current,recommended)
    message.append({
		"uid": str(uuid.uuid4()),
		"updateDate": time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime()),
        "titleText":text, 
        "mainText": text
    })
    
    
    
    text = "接続している端末数は{}台です".format(total_client)
    message.append({
		"uid": str(uuid.uuid4()),
		"updateDate": time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime()),
        "titleText":text, 
        "mainText": text
    })
    
    name = application[0]['name']
    percent = application[0]['percent']
    text = "一番利用量が多いアプリは{}で利用率は{}です".format(name,percent)
    message.append({
		"uid": str(uuid.uuid4()),
		"updateDate": time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime()),
        "titleText":text, 
        "mainText": text
    })

    name = top_client[0]['name']
    rx_bytes = top_client[0]['rx_bytes']
    tx_bytes = top_client[0]['tx_bytes']
    text = "一番利用料が多い端末は{}で利用量は受信が{}バイト、送信が{}バイトです".format(name,rx_bytes,tx_bytes)
    message.append({
		"uid": str(uuid.uuid4()),
		"updateDate": time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime()),
        "titleText":text, 
        "mainText": text
    })

    return message

def lambda_handler(event, context):
    token = read_s3()
    access_token = refresh_token(token)
    ap_status = get_ap_status(access_token)
    total_client = get_total_client(access_token)
    application = get_application(access_token)
    top_client = get_top_client(access_token)
    firmware = get_firmware(access_token)
    message = create_message(ap_status,firmware,total_client,application,top_client)
    text = json.dumps(message, ensure_ascii=False)
    print(text)
    upload_s3(text,"central_message.json")

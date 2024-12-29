
# Input order: shipment_id.csv
# Check log lỗi của đơn hàng.

import requests
import pandas as pd
from tqdm import tqdm
import random
import time
import datetime
from cookies import get_cookies

cookies = get_cookies()

def convert_from_unix_timestamp(unix_timestamp):
    getTime = datetime.datetime.fromtimestamp(unix_timestamp)
    return getTime

# Khai báo data cần lấy.
def parser_data(shipment_id, json):
    d = dict()
    d['shipment_id'] = shipment_id
    d['operate_station_name'] = json.get('operate_station_name')
    d['operator'] = json.get('operator')    
    d['operate_time'] = convert_from_unix_timestamp(int(json.get('operate_time')))
    d['message'] = json.get('message')
    return d

# Lấy shipment_id từ file csv
df_id = pd.read_csv("C:/Users/vu.nguyenduy/OneDrive/Github_mrvu.dev/Crawl_Data/main/shipment_id.csv")
p_ids = df_id.shipment_id.to_list()
result = []

# Kiểm tra requests và xử lý dữ liệu
unsuccessful_url = 'https://spx.shopee.vn/api/fleet_order/order/detail/unsuccessful_operation_log_list?'
r = requests.get(unsuccessful_url, cookies=cookies)
if (r.status_code == 200):
    for pid in tqdm(p_ids, total=len(p_ids)):
        retries = 0
        while retries < 5:
            response = requests.get(unsuccessful_url, params='shipment_id={}&pageno=1&count=100&tdflag=0'.format(pid), cookies=cookies)
            list = response.json().get('data').get('list')
            try:
                for i in range(len(list)):
                    check_shipmentID = list[i]
                    result.append(parser_data(pid, check_shipmentID))
                    print('Crawl data {} success !!!'.format(pid))
                time.sleep(random.randrange(3, 5))
                break
            except AttributeError:
                print('Crawl data {} fail !!!'.format(pid))
                print('Thử lại')
                time.sleep(random.randrange(3, 5))
                retries += 1
        else:
            continue
else:
    print(r.status_code, '--cookies đã hết hạn')

# Xuất ra file csv kết quả
df_product = pd.DataFrame(result)
df_product.to_csv('result/unsuccessful_log_list.csv', encoding='utf-8-sig', index=False)
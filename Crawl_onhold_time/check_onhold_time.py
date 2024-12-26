# Kiểm tra lần cập nhật onhold gần nhất của đơn hàng từ file (shipment_id.csv)

import requests
import pandas as pd
from tqdm import tqdm
import random
import time
import datetime
from Crawl_onhold_time.cookies import get_cookies

cookies = get_cookies()

def convert_from_unix_timestamp(unix_timestamp):
    getTime = datetime.datetime.fromtimestamp(unix_timestamp)
    return getTime

# Khai báo data cần lấy.
def parser_product(json):
    d = dict()
    d['parent_key'] = json.get('parent_key')[:17]
    d['timestamp'] = convert_from_unix_timestamp(json.get('timestamp'))
    d['message'] = json.get('message')
    d['operator'] = json.get('operator')
    return d

 
df_id = pd.read_csv('./shipment_id.csv')
p_ids = df_id.shipment_id.to_list()
result = []

# Kiểm tra requests thành công hay thất bại
tracking_info_url = 'https://spx.shopee.vn/api/fleet_order/order/detail/tracking_info?'
r = requests.get(tracking_info_url, cookies=cookies)
if (r.status_code == 200):
    for pid in tqdm(p_ids, total=len(p_ids)):
        retries = 0
        while retries < 10:
            response = requests.get(tracking_info_url, params='shipment_id={}&station_type=12'.format(pid), cookies=cookies)
            check_shipmentID = response.json().get('data').get('tracking_list')[-1].get('children')
            reverse_list = check_shipmentID[::-1]
            length_list = len(reverse_list)
            time.sleep(random.randrange(1, 3))
            try:
                for i in range(length_list):
                    check_status = reverse_list[i].get('status')
                    if(check_status == 37): #37 is Parcel pickup onhold
                        result.append(parser_product(reverse_list[i]))
                        print('Crawl data {} success !!!'.format(pid))
                        break
                break
            except AttributeError:
                print('Crawl data {} fail !!!'.format(pid))
                print('Thử lại')
                time.sleep(random.randrange(1, 3))
                retries += 1
            except IndexError:
                result.append(parser_product(response.json().get('data').get('tracking_list')[-1]))
                print('Crawl data {} success !!!'.format(pid))
                break
        else:
            continue
else:
    print(r.status_code, '--cookies đã hết hạn')

# Kết quả
df_product = pd.DataFrame(result)
df_product.to_csv('result_OH_time.csv', encoding='utf-8-sig', index=False)
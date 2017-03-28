import json
import requests as rq


def push_data_to_clients():
    try:
        message = "Internet request accepted, Please scan the 7 up barcode."
        target_url = "http://192.168.1.154:8000/push_data_to_clients/"
        data_dict = dict()
        data_dict["success"] = message
        response = rq.post(target_url, data=json.dumps(data_dict))
        print("response status: {}".format(response.status_code))

    except Exception as err:
        print(err.message)




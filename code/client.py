import messages as msg
import json
import sys
import tasks as ts
import os
import sys
import os

def load_json_str(filename):
    with open(filename) as file:
        gjson = json.dumps(json.load(file))
    return gjson

def save_json_str_arr(json_str_arr):
    for i in range(0, len(json_str_arr)):
        with open('map' + str(i) + '.geojson', 'w') as outfile:
            json.dump(json.loads(json_str_arr[i]), outfile)

def receive_callback(ch, method, properties, body):
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
    received_data = body.decode() 
    arr = ts.str_to_list_of_str(received_data)
    save_json_str_arr(arr)
    
    ch.stop_consuming()

def main():  
    filename = sys.argv[1]
    parts_num = int(sys.argv[2])
    gjson_str = load_json_str(filename)
    
    c_f_connection, c_f_channel, c_to_f_queue, f_to_c_queue  = msg.init_client_and_frontend_communication()
    
    message = ts.encode_obj(ts.Envelope(gjson_str, parts_num))
    
    #SEND: client TO frontend
    msg.send(c_f_channel, c_to_f_queue, message)
    print(" [x] Client sent envelope to frontend")
    
    #RECEIVE: client FROM frontend
    msg.receive(c_f_channel, f_to_c_queue, receive_callback)
    print(" [x] Client received maps from frontend")
    
    c_f_connection.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
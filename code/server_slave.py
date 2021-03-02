import messages as msg
import tasks as ts
import crop_map as cm
import sys
import os

def receive_from_master_callback(ch, method, properties, body):

    ch.basic_ack(delivery_tag=method.delivery_tag)
    received_data = ts.decode_obj(body)
    print(" [x] Slave received task from master")
    
    message = ts.json_to_str(cm.crop_map(received_data))
    
    #SEND: slave TO master
    msg.send(m_s_channel, s_to_m_queue, message)
    print(" [x] Slave sent map to master")

def main():  
    
    global m_s_channel, m_to_s_queue, s_to_m_queue
    m_s_connection, m_s_channel, m_to_s_queue, s_to_m_queue = msg.init_master_and_slave_communication()
    
    #RECEIVE: slave FROM master
    msg.receive(m_s_channel, m_to_s_queue, receive_from_master_callback)    
    
    m_s_connection.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

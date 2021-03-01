import messages as msg
import tasks as ts
import crop_map as cm

def receive_from_slave_callback(ch, method, properties, body):

    ch.basic_ack(delivery_tag=method.delivery_tag)
    received_data = body.decode()
    
    splitted_maps.append(received_data)
    
    ch.stop_consuming()

def receive_from_frontend_callback(ch, method, properties, body):
 
    ch.basic_ack(delivery_tag=method.delivery_tag)
    received_data = ts.decode_obj(body)
    print(" [x] Master received envelope from frontend")  
    
    #get number of consumers availible
    queue_state = m_s_channel.queue_declare(queue=m_to_s_queue, durable=True)
 
    workers_num = int(queue_state.method.consumer_count)
    
    gjson = ts.str_to_json(received_data.map_str)
    task_arr = ts.get_tasks(received_data.parts_num, gjson)
    
    #calculate master's portion
    master_portion = len(task_arr) // (workers_num + 1)
    
    for i in range(master_portion, len(task_arr)):
        #SEND: master TO slave
        msg.send(m_s_channel, m_to_s_queue, ts.encode_obj(task_arr[i]))
        print(" [x] Master sent task to slave")
    
    #master does it's work
    splitted_maps.clear()
    for i in range(0, master_portion):
        splitted_maps.append(ts.json_to_str(cm.crop_map(task_arr[i])))
    print(" [x] Master processed it's part of work")
    
    for i in range(master_portion, len(task_arr)):
        #RECEIVE: master FROM slave
        msg.receive(m_s_channel, s_to_m_queue, receive_from_slave_callback)
        print(" [x] Master received map from slave")
    
    #SEND: master TO frontend 
    message = ts.str_list_to_one_str(splitted_maps)
    
    msg.send(f_m_channel, m_to_f_queue, message)
    print(" [x] Master sent maps to frontend")

def main():  
    
    global splitted_maps
    splitted_maps =  []
    
    global current_slaves_count
    global f_m_channel, f_to_m_queue, m_to_f_queue
    global m_s_channel, m_to_s_queue, s_to_m_queue
    f_m_connection, f_m_channel, f_to_m_queue, m_to_f_queue = msg.init_frontend_and_master_communication()
    m_s_connection, m_s_channel, m_to_s_queue, s_to_m_queue = msg.init_master_and_slave_communication()
    
    #RECEIVE: master FROM frontend
    msg.receive(f_m_channel, f_to_m_queue, receive_from_frontend_callback)    
    
    m_s_connection.close()
    f_m_connection.close()

if __name__ == '__main__':
    main()
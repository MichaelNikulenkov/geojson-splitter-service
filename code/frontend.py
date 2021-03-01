import messages as msg
import tasks as ts

def receive_from_master_callback(ch, method, properties, body):
     
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(" [x] Frontend received maps from master") 
    
    message = body.decode()
    
    #SEND: frontend TO cliend 
    msg.send(c_f_channel, f_to_c_queue, message)
    print(" [x] Frontend sent maps to client")
    
    ch.stop_consuming()

def receive_from_client_callback(ch, method, properties, body):

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(" [x] Frontend received body from client")
    received_data = body
    
    message = received_data
    
    #SEND: frontend TO master
    msg.send(f_m_channel, f_to_m_queue, message)
    print(" [x] Frontend sent envelope to master")
    
    #RECEIVE: frontend FROM master
    msg.receive(f_m_channel, m_to_f_queue, receive_from_master_callback)

def main():  
    
    global c_f_channel, c_to_f_queue, f_to_c_queue
    global f_m_channel, f_to_m_queue, m_to_f_queue
    c_f_connection, c_f_channel, c_to_f_queue, f_to_c_queue  = msg.init_client_and_frontend_communication()
    f_m_connection, f_m_channel, f_to_m_queue, m_to_f_queue = msg.init_frontend_and_master_communication()
    
    #RECEIVE: frontend FROM client
    msg.receive(c_f_channel, c_to_f_queue, receive_from_client_callback)
    
    f_m_connection.close()
    c_f_connection.close()

if __name__ == '__main__':
    main()
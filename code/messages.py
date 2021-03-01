import pika
import subprocess
import os
import json

def init_client_and_frontend_communication():
    c_f_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    c_f_channel = c_f_connection.channel()
    
    c_to_f_queue = 'client-frontend_queue'
    c_f_channel.queue_declare(queue=c_to_f_queue, durable=True)
    
    f_to_c_queue = 'frontend-client_queue'
    c_f_channel.queue_declare(queue=f_to_c_queue, durable=True)
    
    return c_f_connection, c_f_channel, c_to_f_queue, f_to_c_queue

def init_frontend_and_master_communication():
    f_m_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    f_m_channel = f_m_connection.channel()
    
    f_to_m_queue = 'frontend-master_queue'
    f_m_channel.queue_declare(queue=f_to_m_queue, durable=True)
    
    m_to_f_queue = 'master-frontend_queue'
    f_m_channel.queue_declare(queue=m_to_f_queue, durable=True)
    
    return f_m_connection, f_m_channel, f_to_m_queue, m_to_f_queue

def init_master_and_slave_communication():
    m_s_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    m_s_channel = m_s_connection.channel()
    
    m_to_s_queue = 'master-slave_queue'
    
    m_s_channel.queue_declare(queue=m_to_s_queue, durable=True)
    #print(queue_state.method.consumer_count)
        
    s_to_m_queue = 'slave-master_queue'
    m_s_channel.queue_declare(queue=s_to_m_queue, durable=True)
    
    return m_s_connection, m_s_channel, m_to_s_queue, s_to_m_queue

def send(channel, queue, message):
    #sent map to frontend
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    
def receive(channel, queue, receive_callback):
    #receive array of maps from frontend
    channel.basic_consume(queue=queue, on_message_callback=receive_callback)
    channel.start_consuming()
import json
import copy
import math
import pickle
import codecs

class Task:
    def __init__(self, xleft, xright, ybottom, ytop, str_gjson):
        self.xleft = xleft
        self.xright = xright
        self.ybottom = ybottom
        self.ytop = ytop
        self.str_gjson = str_gjson

class Envelope:
    def __init__(self, map_str, parts_num):
        self.map_str = map_str
        self.parts_num = parts_num

def str_list_to_one_str(arr):
    whole_string = ""
    for i in range(0, len(arr)):
        whole_string = whole_string + arr[i]
        if i != len(arr) - 1:
            whole_string =  whole_string + "SEPARATOR"
            
    return whole_string
            
def str_to_list_of_str(string):
    return string.split("SEPARATOR")
   
def json_to_str(gjson):
    return json.dumps(gjson)
    
def str_to_json(string):
    return json.loads(string)

def encode_obj(unpickled):
    return pickle.dumps(unpickled)

def decode_list(pickled):
    return str_to_json(pickled)

def encode_list(unpickled):
    #return json_to_str(json.dumps(unpickled))
    return json.dumps(unpickled)

def decode_obj(pickled):
    return pickle.loads(pickled)

def search_borders(gjson):
    xmin = ymin = float('inf')
    xmax = ymax = float('-inf')
    ymin = float('inf')
    ymax = float('-inf')
    
    features = gjson["features"]
    for state in features:
        geometry = state["geometry"]
        geometry_type = geometry["type"]
        
        if geometry_type == "Polygon":
            coordinates = geometry["coordinates"]
            xmin_local = min(coordinates[0], key = lambda x: x[0])[0]
            xmax_local = max(coordinates[0], key = lambda x: x[0])[0]
            ymin_local = min(coordinates[0], key = lambda x: x[1])[1]
            ymax_local = max(coordinates[0], key = lambda x: x[1])[1]
            if xmin_local < xmin:
                xmin = xmin_local
            if xmax_local > xmax:
                xmax = xmax_local
            if ymin_local < ymin:
                ymin = ymin_local
            if ymax_local > ymax:
                ymax = ymax_local
        else:
            coords_arr = geometry["coordinates"]
            for coordinates in coords_arr:
                xmin_local = min(coordinates[0], key = lambda x: x[0])[0]
                xmax_local = max(coordinates[0], key = lambda x: x[0])[0]
                ymin_local = min(coordinates[0], key = lambda x: x[1])[1]
                ymax_local = max(coordinates[0], key = lambda x: x[1])[1]
                if xmin_local < xmin:
                    xmin = xmin_local
                if xmax_local > xmax:
                    xmax = xmax_local
                if ymin_local < ymin:
                    ymin = ymin_local
                if ymax_local > ymax:
                    ymax = ymax_local   
                    
    
    return xmin, xmax, ymin, ymax

def get_grid_dim(parts_num):
    
    #check if parts_num is a prime number
    is_prime = True
    for i in range(2, parts_num):
       if (parts_num % i) == 0:
        is_prime = False
    
    if not is_prime:
        #find best dimensions
        dim_x = int(math.sqrt(parts_num))
        dim_y = parts_num // dim_x
    else:
        dim_x = 1
        dim_y = parts_num
        
    return dim_x, dim_y
           
def get_tasks(parts_num, gjson):
    dim_x, dim_y = get_grid_dim(parts_num)
    xmin, xmax, ymin, ymax = search_borders(gjson)
    
    xstep = abs(xmax - xmin) / dim_x
    ystep = abs(ymax - ymin) / dim_y
    
    task_arr = []
    
    for i in range(0, dim_x):
        for j in range(0, dim_y):
            xleft = xmin + i * xstep
            xright = xmin + (i + 1) * xstep
            ybottom = ymin + j * ystep
            ytop = ymin + (j + 1) * ystep
            task_arr.append(Task(xleft, xright, ybottom, ytop, json_to_str(gjson)))
    
    return task_arr
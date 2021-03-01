import tasks as ts
import json
import copy
from geojson_rewind import rewind

def is_square(apositiveint):
  x = apositiveint // 2
  seen = set([x])
  while x * x != apositiveint:
    x = (x + (apositiveint // x)) // 2
    if x in seen: return False
    seen.add(x)
  return True

def scan_coords_y(coordinates, bottom, top):
    new_coordinates = []
    for i in range(0, len(coordinates)):
        xcurr = coordinates[i][0]
        ycurr = coordinates[i][1]
        if ycurr >= bottom and ycurr <= top:
            if i > 0:  
                xprev = coordinates[i - 1][0]
                yprev = coordinates[i - 1][1]
                if not (yprev >= bottom and yprev <= top):
                    #calculate intersection
                    x1 = xprev
                    y1 = yprev
                    x2 = xcurr
                    y2 = ycurr
                    y = bottom if yprev < bottom else top
                    k = (x2 - x1) / (y2 - y1)
                    x = x1 + (y - y1) * k 
                    new_coordinates.append([copy.deepcopy(x), copy.deepcopy(y)])
                              
            new_coordinates.append(coordinates[i])
        else:
            if i > 0:
                xprev = coordinates[i - 1][0]
                yprev = coordinates[i - 1][1]
                if yprev >= bottom and yprev <= top:
                    #calculate intersection
                    x1 = xprev
                    y1 = yprev
                    x2 = xcurr
                    y2 = ycurr
                    y = bottom if ycurr < bottom else top
                    k = (x2 - x1) / (y2 - y1)
                    x = x1 + (y - y1) * k
                    new_coordinates.append([copy.deepcopy(x), copy.deepcopy(y)]) 
                        
    #check if first and last points are identical     
    if new_coordinates:
        if (new_coordinates[0][0] != new_coordinates[-1][0]) or (new_coordinates[0][1] != new_coordinates[-1][1]):
            new_coordinates.append(new_coordinates[0])
    
    return new_coordinates

def scan_coords_x(coordinates, bottom, top):
    new_coordinates = []
    for i in range(0, len(coordinates)):
        xcurr = coordinates[i][0]
        ycurr = coordinates[i][1]
        if xcurr >= bottom and xcurr <= top:
            if i > 0:  
                xprev = coordinates[i - 1][0]
                yprev = coordinates[i - 1][1]
                if not (xprev >= bottom and xprev <= top):
                    #calculate intersection
                    x1 = xprev
                    y1 = yprev
                    x2 = xcurr
                    y2 = ycurr
                    x = bottom if xprev < bottom else top
                    m = (y2 - y1) / (x2 - x1)
                    y = y1 + m * (x - x1)
                    new_coordinates.append([copy.deepcopy(x), copy.deepcopy(y)])
                                   
            new_coordinates.append(coordinates[i])
        else:
            if i > 0:
                xprev = coordinates[i - 1][0]
                yprev = coordinates[i - 1][1]
                if xprev >= bottom and xprev <= top:
                    #calculate intersection
                    x1 = xprev
                    y1 = yprev
                    x2 = xcurr
                    y2 = ycurr
                    x = bottom if xcurr < bottom else top
                    m = (y2 - y1) / (x2 - x1)
                    y = y1 + m * (x - x1)
                    new_coordinates.append([copy.deepcopy(x), copy.deepcopy(y)]) 
                        
    #check if first and last points are identical     
    if new_coordinates:
        if (new_coordinates[0][0] != new_coordinates[-1][0]) or (new_coordinates[0][1] != new_coordinates[-1][1]):
            new_coordinates.append(new_coordinates[0])
    
    return new_coordinates

def fit_y(gjson, ybottom, ytop):
    fitted_gjson = copy.deepcopy(gjson)
    fitted_gjson["features"] = []
    
    features = gjson["features"]
    for state in features:
    
        geometry = state["geometry"]
        geometry_type = geometry["type"]
        
        if geometry_type == "Polygon":
            
            coordinates = geometry["coordinates"]
            new_coordinates = scan_coords_y(coordinates[0], ybottom, ytop)
                        
            if new_coordinates:
                fitted_gjson["features"].append(state)
                fitted_gjson["features"][-1]["geometry"]["coordinates"] = [new_coordinates]
        else:
            
            #if state is a multipolygon
            coords_arr = geometry["coordinates"][0]
            new_coords_arr = []
            
            for coordinates in coords_arr:
                new_coordinates = scan_coords_y(coordinates, ybottom, ytop)
                new_coords_arr.append(new_coordinates) 
            
            not_empty_poly_count = 0
            flag_arr = []
            for coordinates in new_coords_arr:
                if coordinates:
                    not_empty_poly_count += 1
                    flag_arr.append(True)
                else:
                    flag_arr.append(False)
            
            if not_empty_poly_count > 1:
                
                fitted_gjson["features"].append(state)
                fitted_gjson["features"][-1]["geometry"]["coordinates"] = [[]]
                
                for i in range(0, len(flag_arr)):
                    if flag_arr[i] == True:
                        fitted_gjson["features"][-1]["geometry"]["coordinates"][-1].append(new_coords_arr[i])
                
            elif not_empty_poly_count != 0:
                #if state turns to polygon
                for i in range(0, len(flag_arr)):
                    if flag_arr[i] == True:
                        not_empty_index = i
                
                fitted_gjson["features"].append(state)
                fitted_gjson["features"][-1]["geometry"]["type"] = "Polygon"
                fitted_gjson["features"][-1]["geometry"]["coordinates"] = [new_coords_arr[not_empty_index]]
     
    return fitted_gjson

def fit_x(gjson, xleft, xright):
    fitted_gjson = copy.deepcopy(gjson)
    fitted_gjson["features"] = []
    
    features = gjson["features"]
    for state in features:
        
        geometry = state["geometry"]
        geometry_type = geometry["type"]
        
        if geometry_type == "Polygon":
            coordinates = geometry["coordinates"]
            new_coordinates = scan_coords_x(coordinates[0], xleft, xright)
                        
            if new_coordinates:
                fitted_gjson["features"].append(state)
                fitted_gjson["features"][-1]["geometry"]["coordinates"] = [new_coordinates]
        else:
            #if state is a multipolygon
            coords_arr = geometry["coordinates"]
            new_coords_arr = []
            
            for coordinates in coords_arr:
                new_coordinates = scan_coords_x(coordinates[0], xleft, xright)
                new_coords_arr.append(new_coordinates) 
            
            not_empty_poly_count = 0
            flag_arr = []
            for coordinates in new_coords_arr:
                if coordinates:
                    not_empty_poly_count += 1
                    flag_arr.append(True)
                else:
                    flag_arr.append(False)
            
            if not_empty_poly_count > 1:
                
                fitted_gjson["features"].append(state)
                fitted_gjson["features"][-1]["geometry"]["coordinates"] = [[]]
                
                for i in range(0, len(flag_arr)):
                    if flag_arr[i] == True:
                        fitted_gjson["features"][-1]["geometry"]["coordinates"][-1].append(new_coords_arr[i])
                
            elif not_empty_poly_count != 0:
                #if state turns to polygon
                for i in range(0, len(flag_arr)):
                    if flag_arr[i] == True:
                        not_empty_index = i
                
                fitted_gjson["features"].append(state)
                fitted_gjson["features"][-1]["geometry"]["type"] = "Polygon"
                fitted_gjson["features"][-1]["geometry"]["coordinates"] = [new_coords_arr[not_empty_index]]
            
    return fitted_gjson

def fit_gjson(gjson, xleft, xright, ybottom, ytop):
    fitted_x = fit_x(copy.deepcopy(gjson), xleft, xright)
    fitted_gjson = fit_y(copy.deepcopy(fitted_x), ybottom, ytop)
    return rewind(fitted_gjson)

def crop_map(task):
    return fit_gjson(rewind(ts.str_to_json(task.str_gjson)), task.xleft, task.xright, task.ybottom, task.ytop)
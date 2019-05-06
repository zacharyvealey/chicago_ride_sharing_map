import csv
import math
import pickle
import folium
from collections import Counter
from datetime import date, timedelta, datetime

def extract_last_week(filename, last_day):
    """
        A function to extract the Chicago ride sharing information for the week
        prior to that specified for the last day.
    """
    reader = csv.reader(open(filename), delimiter = ',')
    next(reader)
    past_week = []

    for i in range(7):
        past_week.append((last_day - timedelta(i)).__format__('%m/%d/%Y'))
    
    data = []
    
    for i, row in enumerate(reader):
        if row[1].split()[0] in past_week:
            data.append(row)
    
    date_sort = sorted(data, key=lambda row: \
                datetime.strptime(row[1], '%m/%d/%Y %H:%M'), reverse=True)
    
    with open('last_week_data.txt', 'wb') as fp:
        pickle.dump(date_sort, fp)

def convert_hour(counter_output):
    """
        Converts the ouput of a Counter's most common function for dictionaries
        into a timestamp.
    """
    if int(counter_output[0][0]) == 0:
        time = '12 AM'
    elif int(counter_output[0][0]) < 12:
        time = counter_output[0][0] + ' AM'
    elif int(counter_output[0][0]) == 12:
        time = '12 PM'
    elif int(counter_output[0][0]) > 12:
        time = str(int(counter_output[0][0])-12) + ' PM'
        
    return time
    
def plot_last_day(filename):
    """
        A function that plots the location and amounts of rides taken on the 
        last day of the week from the data extracted in the extract_last_week
        function.
    """
    with open (filename, 'rb') as fp:
        date_sort = pickle.load(fp)
        
        locations = {}
        
        # Look at last day for the moment
        #last_day = date_sort[0][1].split()[0]
        
        for row in date_sort:
            if row[1].split()[0] == '12/15/2018' or row[1].split()[0] == '12/12/2018':
                continue
            
            if row[1].split()[0] == '12/13/2018':
                break
            
            if row[15] and row[16]:
                p_time = datetime.strptime(row[1].split()[1], '%H:%M')
                hour = row[1].split()[1].split(':')[0]
                
                if (float(row[15]), float(row[16])) in locations:
                    locations[(float(row[15]), float(row[16]))][0] += 1
                    if hour in locations[(float(row[15]), float(row[16]))][1]:
                        locations[(float(row[15]), float(row[16]))][1][hour] += 1
                    else:
                        locations[(float(row[15]), float(row[16]))][1][hour] = 1
                else:
                    locations[(float(row[15]), float(row[16]))] = [1,{hour:1}]
            
    # Map of Chicago.
    chicago = folium.Map(location=[41.895140898, -87.624255632],
                            zoom_start=13,tiles="CartoDB dark_matter")
    
    # Circle Markers 
    for key, val in locations.items():
        most_common_hour = Counter(val[1]).most_common(1)
                
        msg = "Pickups: " + str(val[0]) + "\n"
        msg += "Time: " + convert_hour(most_common_hour)
        msg += "Location: " + str(key[0]) + " " + str(key[1])
        
        colors = {'0': '#010CA7', '1': '#310AB4', '2': '#6108C1', '3': '#9106CE',
            '4': '#C104DB', '5': '#F202E9', '6': '#E5D800', '7': '#DEB600',
            '8': '#D89400', '9': '#D27300', '10': '#CB5100', '11': '#C52F00',
            '12': '#BF0E00', '13': '#C9290F', '14': '#D4441E', '15': '#DF602E',
            '16': '#E97B3D', '17': '#F4964C', '18': '#FFB25C', '19': '#00ACBF',
            '20': '#008CBA', '21': '#006CB5', '22': '#004CB0', '23': '#002CAB',
            }
        
        
        folium.CircleMarker([key[0], key[1]],color=colors[most_common_hour[0][0]],
                                tooltip = msg, radius=val[0]/20,
                                fill=True).add_to(chicago)
            
    # Save method of Map object will create a map 
    chicago.save("chicago2.html" ) 

def loc_by_time(filename, location):
    with open (filename, 'rb') as fp:
        date_sort = pickle.load(fp)
        
        loc_freq = {}
        
        for row in date_sort:
            if row[1] and row[15] and row[16] and float(row[15]) == location[0]\
            and float(row[16]) == location[1]:
                if row[1] in loc_freq:
                    loc_freq[row[1]] += 1
                else:
                    loc_freq[row[1]] = 1
    
    name = "night_" + str(location[0]) + "_" + str(location[1]) + ".dat"            
    f = open(name, "w")
    f.write("Date_" + str(location[0]) + "_" + str(location[1]) + "\t" + 
                "Freq_" + str(location[0]) + "_" + str(location[1]) + "\n")
    
    for key, val in loc_freq.items():
        f.write(key + "\t" + str(val) + "\n")
        
    f.close()
    

extract_last_week('Transportation_Network_Providers_-_Trips.csv', date(2018, 12, 15))
plot_last_day('last_week_data.txt')

day_locs = [[41.88099447,-87.63274649],[41.89321636,-87.63784421],
            [41.88530002,-87.64280847],[41.87925508,-87.642649]]
night_locs = [[41.89204214,-87.63186395],[41.88528132,-87.6572332],
                [41.88498719,-87.62099291],[41.89250778,-87.62621491]]
                
#loc_by_time('last_week_data.txt', [41.88099447,-87.63274649])

for loc in night_locs:
    loc_by_time('last_week_data.txt', loc)


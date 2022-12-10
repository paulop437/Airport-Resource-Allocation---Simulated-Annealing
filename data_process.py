import random

import pandas as pd
from Evento import Evento

columns=["flight_icao","dep_icao","arr_icao","arr_time_ts","dep_time_ts"]
gates=["Gate 1","Gate 2","Gate 3","Gate 4","Gate 5"]
df = pd.read_csv("./data.csv",usecols=columns)

departures = df[df.dep_icao == "LPPD"]
arrivals = df[df.arr_icao == "LPPD"]

event_list = []

for index,arrival in arrivals.iterrows():
    #Relacionar estas randomizations com o size do flight
    estimated_dur = random.randint(15,25) #Tempo necessário to be completed
    priority = random.randint(1,2) #Prioridade definida
    event_list.append(Evento("Sala de Bagagens", 2, arrival[3], estimated_dur, "aguarda",0, 0, priority,"arrival"))

for index,departure in departures.iterrows():
    gate_choice = gates[random.randint(0,4)]
    workers = random.randint(4,8) # Número de workers necessários
    estimated_dur = random.randint(10, 30)  # Tempo necessário to be completed
    priority = random.randint(0, 2)  # Prioridade definida
    event_list.append(Evento(gate_choice, workers, departure[4], estimated_dur, "aguarda",0, 0, priority, "departure"))

#Ordenar eventos com base no start_time
new_list = sorted(event_list, key=lambda x:x.start_time)

print(new_list)

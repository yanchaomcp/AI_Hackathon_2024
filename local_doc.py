# This document describes the creation of a `mock dataset` that simulates comprehensive travel information 
# for various origins, destinations, and modes of transport. 
# The dataset is designed to serve as a `substitute for real-time API data`, 
# supporting user-preference-based `travel mode recommendations`.
    

import pandas as pd
import random
random.seed(1024)
path = "C:\\Users\\qc_wo\\Desktop\\" 

# Generate a list of locations
locations = [ "Central_Park", "Times_Square", "NYU_Tandon","Brooklyn_Bridge"]

# Travel modes
modes = ["Drive", "Ride-hailing", "Citi_bike", "Public_transit"]

# Generate random OD pairs and travel details for each mode
data = []
for origin in locations:
    for destination in locations:
        if origin != destination:
            for mode in modes:
                if mode == "Drive":
                    time_cost = random.randint(10, 40)
                    fare_cost = round(random.uniform(5, 20), 2)
                    co2_cost = round(random.uniform(10, 30), 2)
                    energy_cost = random.randint(50, 200) # Walking distance in meters
                elif mode == "Ride-hailing":
                    time_cost = random.randint(15, 50)
                    fare_cost = round(random.uniform(10, 40), 2)
                    co2_cost = round(random.uniform(5, 15), 2)
                    energy_cost = random.randint(20, 80) 
                elif mode == "Citi_bike":
                    time_cost = random.randint(20, 60)
                    fare_cost = round(random.uniform(3.5, 5), 2)
                    co2_cost = round(random.uniform(0.1, 1.0), 2)
                    energy_cost = random.randint(200, 1000)  
                elif mode == "Public_transit":
                    time_cost = random.randint(25, 75)
                    fare_cost = round(random.uniform(2.7, 5), 2)
                    co2_cost = round(random.uniform(1, 5), 2)
                    energy_cost = random.randint(300, 1500)  

                data.append([origin, destination, mode, time_cost, fare_cost, co2_cost, energy_cost])

# Create a DataFrame
df = pd.DataFrame(data, columns=["origin", "destination", "mode", "time_cost", "fare_cost", "co2_cost", "energy_cost"])

# Save the dataset to a CSV file
df.to_csv(f"{path}travel_data.csv", index=False)
print("Artificial dataset with travel modes generated and saved as 'travel_data.csv'.")
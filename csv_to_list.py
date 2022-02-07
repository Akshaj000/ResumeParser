import csv

city_state_file = open("Assets/india_cities_states_feb_2015.csv", "r")

reader = csv.reader(city_state_file)
city = []
state = []
for row in reader:
    city.append(row[0])
    state.append(row[1])
print(city,state)
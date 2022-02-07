import csv

city_state_file = open("Assets/states.csv", "r")

reader = csv.reader(city_state_file)
state = []
for row in reader:
    state.append(row[0])
print(state)
teams = []

n = int(input("How many teams are there? "))

for i in range(n):
    team = input(f"Enter team ranked #{i + 1}: ")
    teams.append(team)

ranking = {}

for i in range(n):
    ranking[teams[i]] = i + 1

print("\nEnter game results.")
print("For each game, enter the winner and loser.\n")

games = int(input("How many games were played? "))

upsets = 0

for i in range(games):
    print(f"\nGame {i + 1}")

    winner = input("Winner: ")
    loser = input("Loser: ")

    if ranking[winner] > ranking[loser]:
        upsets += 1
        print("Upset!")
    else:
        print("Not an upset.")

frequency = upsets / games

print("\nResults")
print("Total games:", games)
print("Total upsets:", upsets)
print("Upset frequency:", frequency)
print("Upset percentage:", frequency * 100, "%")
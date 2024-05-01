import csv
import time
import operator
import random
import os
import threading
import sys

from time import sleep
from datetime import datetime


user_profiles = {}
active_users = {
        "player1":{"username": "waiting..."},
        "player2": {"username": "waiting..."}
    }


# ================================================================================
# 1. MAIN GAME LOGIC
# ================================================================================

def gameplay():
    """Runs through the game. The function calls on returnPopulatedUserProfiles() to read 
    the 'user_data.csv' file into the global 'user_profiles' variable. After which, 
    it calls on the displayLeaderboard() function and the P1_P2_login() function to prompt for the user
    to select an action.

    The function then continues to call the promptUserForGame() function until the lives of either player1 
    or player2 reach 0, after which the elo and wins for each player is updated using the elo_and_wins_update() 
    function. Lastly, the function calls on the saveUserProfileToCSV() function output the updated player
    information to a csv file and displays the leaderboard before finally returning, and thus ending
    the execution of the program.
    
    """    
    global user_profiles
    user_profiles = returnPopulatedUserProfiles()
    outcome = {}
    displayLeaderboard()
    clearScreenAfterDelay(3)
    P1_P2_login()
    while active_users['player1']['global_lives'] > 0 and active_users['player2']['global_lives'] > 0:
        promptUserForGame()
    if active_users['player1']['global_lives'] == 0:
        outcome = {"P1": 0, "P2": 1}
    elif active_users['player2']['global_lives'] == 0:
        outcome = {"P1": 1, "P2": 0}
    p1_rating = user_profiles[active_users["player1"]["username"]]['elo']
    p2_rating = user_profiles[active_users["player2"]["username"]]['elo']
    elo_and_wins_update(p1_rating, p2_rating, outcome)
    saveUserProfileToCSV()
    print('GAME OVER, THANK YOU FOR PLAYING!')
    displayLeaderboard()
    return

# ================================================================================
# 2. USER MANAGEMENT SYSTEM
# ================================================================================

def returnPopulatedUserProfiles():
    """
    Reads the csv file user_data.csv and processes the items into
    a dictionary called 'user_profiles' which the function returns. 

    Returns:
        dict: 'user_profiles' dictionary with user's username as key and value as a dictionary 
        with their elo number of wins.
    """    
    with open('user_data.csv', 'r') as user_data_file:
        csv_reader = csv.DictReader(user_data_file, delimiter=',')

        for row in csv_reader:
            user_profiles[row['username']] = {
                'elo': int(row['elo']),
                'wins': int(row['wins'])
            }

    return user_profiles

def saveUserProfileToCSV():
    """
    Overwrites the user_data.csv file with the updated information from the 'user_profiles' dictionary.
    """    
    with open('user_data.csv', 'w') as user_data_file:
        csv_writer = csv.writer(user_data_file, delimiter=',')
        
        # Writing the headers
        csv_writer.writerow(['username', 'elo', 'wins'])

        for user in user_profiles:
            csv_writer.writerow([user, user_profiles[user]['elo'], user_profiles[user]['wins']])

def displayLeaderboard():
    """Displays the top 10 user profiles, sorted according to their elo scores.
    """
    sorted_user_profiles = sorted(user_profiles.items(), key=lambda x: x[1]['elo'], reverse=True)
    print("═══════════════ TOP 10 ═══════════════")
    for index in range(len(sorted_user_profiles[0:10])):
        user = sorted_user_profiles[index]
        rank = index + 1
        print(f" Rank {rank} ({user[1]['elo']}) {user[0]}, Wins: {user[1]['wins']} ")
    print("══════════════════════════════════════")

# B. LOGIN FUNCTION
def Login_Signup(user_profiles: dict, player: int):
    """Prompts the user to login, signup or view the leaderboard. Used to get the user information for gameplay when logging in,
        to populate the global user_profiles dictionary with a user name and default player statistics {"elo": 1500, "wins":0} when signing up. 
        Reprompts user to login or signup if an invalid username or action is input. 

    Args:
        user_profiles (dict): A dictionary containing the information of users in the following format {"username":{"elo":x,"wins":x}}

    Returns:
        list: upon a succesful login it returns a list containing True and the username inputted. In the format
        [True, "username"]
    """    
    while True:
        print("┌─────────────────────────────────────┐")
        print("│ leaderboard ║ signup ║ login ║ quit │")
        print("└─────────────────────────────────────┘")
        LS_decision = input("Please select an option: ").lower()
        # Signup 
        if LS_decision == "signup":
            clearScreenAfterDelay(0)
            sucessful_signup = False
            while True:
                print("Press enter to return to previous.")
                signup_username = input("Please enter a username to signup: ")
                if signup_username in user_profiles:
                    # Display Username taken error
                    clearScreenAfterDelay(0)
                    print("Username already taken. Please try again.")
                    continue

                elif len(signup_username) == 0:
                    clearScreenAfterDelay(0)
                    print("Returned to previous.")
                    break

                elif len(signup_username) != 0 and not signup_username in user_profiles:
                    user_profiles[signup_username] = {"elo":1500,"wins":0}
                    sucessful_signup = True
                    break

            if sucessful_signup == True:
                clearScreenAfterDelay(0)
                # Display Sucessful signup message
                print("Signup successful! Please login.")
                continue
                
        # Login
        elif LS_decision == "login":
            clearScreenAfterDelay(0)
            print("Note: Username is CaseSensitive.")
            login_username = input("Please enter a username to login: ") 
            sucessful_login = False
            if login_username in user_profiles and login_username != active_users["player1"]["username"]:
                sucessful_login = True

            if sucessful_login:
                clearScreenAfterDelay(0)
                # Display welcome message (or other action)
                print(f"Welcome {login_username} you are PLAYER {player}")
                clearScreenAfterDelay(1)
                return [True, login_username]

            else:
                clearScreenAfterDelay(0)
                print("Username not found or already assigned to a player. Please try again or signup.")
                continue
        
        # leaderboard Input
        elif LS_decision == "leaderboard":
            displayLeaderboard()
            print("(This leaderboard will be displayed for 5 seconds.)")
            clearScreenAfterDelay(5)
            continue

        # quit Input
        elif LS_decision == "quit":
            saveUserProfileToCSV()
            clearScreenAfterDelay(0)
            sys.exit()

        # Invalid Input
        else:
            clearScreenAfterDelay(0)
            print("invalid selection please enter 'login' or 'signup'")
            continue

def P1_P2_login():
    """Repeats the Login_Signup function twice for player1 and player 2.
        uses the information retrieved from the Login_Signup function to populate the global active_users dictionary with the username and 
        default starting lives of 3. In the format: 
        {"player1":{"username":"xxxx","global_lives":3},"player1":{"username":"xxxx",global_lives":3}}
        also displays the game's title "BRAINBuddy". The function does not take any inputs.
    """    
    for i in range(2):   
        print("╔════════════════════════════════════════════════════════╗")
        print("║ ____            _     _____          _                 ║")
        print("║| __ ) _ __ __ _(_)_ _|_   _| __ __ _(_)_ __   ___ _ __ ║")
        print("║|  _ \| '__/ _` | | '_ \| || '__/ _` | | '_ \ / _ \ '__|║")
        print("║| |_) | | | (_| | | | | | || | | (_| | | | | |  __/ |   ║")
        print("║|____/|_|  \__,_|_|_| |_|_||_|  \__,_|_|_| |_|\___|_|   ║")
        print("╚════════════════════════════════════════════════════════╝")                                  
        print(f"PLAYER 1 ({active_users['player1']['username']}) vs PLAYER 2 ({active_users['player2']['username']})")
        result = Login_Signup(user_profiles, i+1)
        if result[0] == True:
            active_users[f'player{i+1}'] = {"username":result[1],"global_lives":3}

# Adapted from https://stackoverflow.com/questions/2084508/clear-terminal-in-python
def clearScreenAfterDelay(delay=3):
    """Clears the screen after a specified delay.

    Args:
        delay (int, optional): The number of seconds to wait before clearing the screen. Defaults to 3.
    """    
    sleep(delay)
    os.system('cls' if os.name == 'nt' else 'clear')

# C. ELO
def elo_and_wins_update(P1_rating: int, P2_rating: int, outcome: dict):
    """ Calculates a player's new elo and win after game is concluded. 
        Updates the new calculated elo and wins to the global user_profile dictionary.

    Args:
        P1_rating (int): The integer value of player1's elo, obtained from the user_profiles dictionary
        P2_rating (int): The integer value of player2's elo, obtained from the user_profiles dictionary
        outcome (dict): dictionary containing who won or lost the game. 
                        example of outcome dictionary format: {"P1":1, "P2":0} (1 for won and 0 for lost.)
    """ 
    # prob of winning
    P1_prob = 1/(10**((P2_rating - P1_rating)/400)+1)
    P2_prob = 1 - P1_prob
    # elo update 
    P1_rating += 30*(outcome["P1"] - P1_prob)
    P2_rating += 30*(outcome["P2"] - P2_prob)
    # Updating user data elo
    user_profiles[active_users["player1"]["username"]]["elo"] = round(P1_rating)
    user_profiles[active_users["player2"]["username"]]["elo"] = round(P2_rating)
    # Updating user data wins
    user_profiles[active_users["player1"]["username"]]["wins"] += outcome["P1"]
    user_profiles[active_users["player2"]["username"]]["wins"] += outcome["P2"]
    


# ================================================================================
# 3. HANG MAN
# ================================================================================

hangman_outcome = {"P1":0,"P2":0}

def hangman(word: str, player: int, round: int, country: str):
    """Inititiates the basic hangman game and logic. prompts user for a character input to guess the selected word.
       prints "correct!" for correct guesses and returns error messages for invalid inputs (such as spaces or empty inputs). 
       user is allowed to enter 'hint' to get a hint (function populates one of the blinded letters). 

    Args:
        word (str): A string representing the word or country's capital to be guessed.
        player (int): an int representing the player number (1 or 2) used for the interface and as keys in user dictionaries
        round (int): an int representing the current round number, used for the interface
        country (str): a string of a randomly chosen country name, which will be used as a key for the get_countries dictionaries
    """    
    word = word.lower()
    hints = 3
    local_lives = 7 
    decompressed = ''
    for i in range(len(word)):
        decompressed += word[i] + ' '
    answer_ls = list(decompressed)
    hint_ls = [*set(list(word.replace(" ", "")))]
    blinded_ls = []
    guesses = []
    for i in answer_ls:
        if i != " ":
            blinded_ls.append("_")
        elif i == " ":
            blinded_ls.append(i)
    # Hangman portion
    while True:
        clearScreenAfterDelay(0.5)
        print(f"Player {player}: {active_users[f'player{player}']['username']}  Round: {round}/3  Score: {hangman_outcome[f'P{player}']}\n")
        print(f"What's the capital city of {country}?")
        print(f"Wrong Guesses: {guesses}")
        print(" ")
        print("".join(blinded_ls))
        if answer_ls[:] == blinded_ls[:]:
            hangman_outcome[f"P{player}"] += 50
            print("nice!")
            break
        print(" ")
        print (f"[Chances remaining: {local_lives}] [Hints remaining: {hints}]\n")
        print("enter 'hint' for a hint. (-10 pts)")
        user_answer = input("Please enter a letter to guess: ").lower()
        if user_answer == "hint" and hints > 0:
            hints += -1
            hangman_outcome[f"P{player}"] += -10
            user_answer = random.choice(hint_ls)
            try:
                hint_ls.remove(user_answer)
            except:
                hint_ls
            for i in range(len(answer_ls)-1):
                if answer_ls[i] == user_answer:
                    blinded_ls[i] = answer_ls[i]
            continue

        elif len(user_answer) > 1 or len(user_answer) == 0 or user_answer == " ":
            print("Invalid input. Please enter a single letter.")
            continue
        elif user_answer in answer_ls:
            try:
                hint_ls.remove(user_answer)
            except:
                hint_ls
            for i in range(len(answer_ls)-1):
                if answer_ls[i] == user_answer:
                    blinded_ls[i] = answer_ls[i]
            print("correct!")
            continue
        elif local_lives == 0:
            clearScreenAfterDelay(0)
            print("Out of chances!")
            print(f"'What's the capital city of {country}?'")
            print(f"Correct answer: {word.upper()} ")
            sleep(5)
            break
        elif not user_answer in answer_ls:
            print("incorrect guess")
            if not user_answer in guesses:
                guesses.append(user_answer)
                local_lives += -1 
            continue


def P1_P2_hangman():
    """P1_P2_hangman() takes no arguments or inputs;
       it repeats the hangman() function a total of 6 times for 6 total rounds of hangman. (3 rounds for player 1 and 3 rounds for player 2).
       Upon completion of the 6 rounds, the function compares the player 1 and player 2's scores and determines a winner or a draw.
       In the event of a draw, function does not update global lives. If a winner is determined, the loser loses a global life. 
    """    
    for i in range(2):
        for round in range(3):
            # replace random test words with geo data
            country_dict = get_country_dict()
            random_country = random.choice(list(country_dict.keys()))
            word_to_guess = country_dict[random_country][0]
            hangman(word_to_guess,(i+1),(round+1), random_country)
    clearScreenAfterDelay(0)
    print(f"FINAL SCORE: (P1: {hangman_outcome['P1']}) vs (P2: {hangman_outcome['P2']})")
    if hangman_outcome["P1"] == hangman_outcome["P2"]:
        print("Its a DRAW!")
    elif hangman_outcome["P1"] > hangman_outcome["P2"]:
        print("P1 WINS!")
        active_users['player2']['global_lives'] -= 1
    elif hangman_outcome["P1"] < hangman_outcome["P2"]:
        print("P2 WINS!")
        active_users['player1']['global_lives'] -= 1

# ================================================================================
# 4. HIGHER LOWER
# ================================================================================

def higher_lower():
    """
    This function calls the one_player() function for each player to play the game. The returned score is then used to determine who won.
    The player who lost would have one of their global life deducted and the player's individual global lives left would then be shown.
    """
    # get player username:
    player1 = active_users['player1']
    player2 = active_users['player2']

    clearScreenAfterDelay(0)

    print(f'First player: {player1["username"]}\n')
    player1_score = one_player()
    print(f'\nSecond player: {player2["username"]}\n')
    player2_score = one_player()
    print('------------------------------------------')
    print(f"\n{player1['username']}'s total score: {player1_score}\n{player2['username']}'s total score: {player2_score}\n")
    if player1_score > player2_score:
        print(f'Congratulations! {player1["username"]} won :D')
        player2["global_lives"] -= 1
    elif player1_score < player2_score:
        print(f'Congratulations! {player2["username"]} won :D')
        player1["global_lives"] -= 1
    else:
        print("It's a draw!")
    print('----------------------------')
    print(f"Total lives left:\n{player1['username']} = {player1['global_lives']}\n{player2['username']} = {player2['global_lives']}")

    clearScreenAfterDelay(3)


def one_player():
    """This function first calls the get_country_dict() function to retrieves a country dictionary containing the population and city of each country.
    A while loop is used to consecutively launch questions until a player gets a question wrong.
    In the while loop, it calls the choice() function which randomly chooses a country with its city and population, from the country dictionary.
    The question on which given city has a higher or lower population is then prompted and a point is awarded if their given answer matches our calculations.

    Returns:
        int: total points
    """
    country_dict = get_country_dict()

    rounds = 0
    game_over = False
    while not game_over:
        country1, city1, population1 = choice(country_dict)
        country2, city2, population2 = choice(country_dict)

        player_answer = input(
            f'Does the city {city1} from {country1} have a higher or lower population than the city {city2} from {country2}?  (higher/lower) ')
        difference = population1 - population2

        # correct conditions:
        higher_correct = (player_answer.lower() == 'higher') and (difference > 0)
        lower_correct = (player_answer.lower() == 'lower') and (difference < 0)

        # wrong conditions:
        higher_wrong = (player_answer.lower() == 'higher') and (difference < 0)
        lower_wrong = (player_answer.lower() == 'lower') and (difference > 0)

        if higher_correct or lower_correct:
            print('Yay, Correct! :)')
            print(f'Population of {city1} from {country1} is: {population1}')
            print(f'Population of {city2} from {country2} is: {population2}')
            clearScreenAfterDelay(1)
            rounds += 1
        elif higher_wrong or lower_wrong:
            print('Nope, incorrect! :(')
            print(f'Population of {city1} from {country1} is: {population1}')
            print(f'Population of {city2} from {country2} is: {population2}\n')
            print('GAME OVER')
            clearScreenAfterDelay(2)
            break
        else:
            print('Input not accepted, please try again.')
    print(f'Your total score: {rounds}')  # write result into another file for leaderboard
    clearScreenAfterDelay(3)
    return rounds


def get_country_dict():
    """This function opens and reads the csv file as a dictionary. 
    The data is then reassigned to a new dictionary (country_dict), where country is the key while city and population are the values.

    Returns:
        dict: dictionary where country is the key while city and population are the values
    """
    filename = 'game_data.csv'
    with open(filename) as file:
        csvreader = csv.DictReader(file)
        country_dict = {}
        for row in csvreader:
            country_values = row['country']
            city_values = row['city']
            population_values = row['population']

            # new dict: key = country_values, value = list of [city_values, population_values]
            country_dict[country_values] = [city_values, population_values]
    return country_dict

def choice(country_dict):
    """This function randomly chooses a country with its city and population, from the country dictionary.
    To avoid repeated questions, the chosen country would be removed from the country dictionary.

    Args:
        country_dict (dict): dictionary where country is the key while city and population are the values

    Returns:
        str: the randomly chosen country and its city
        int: population of the randomly chosen country
    """
    choice1 = random.choice(list(country_dict.items()))
    choice1_country, choice1_city, choice1_population = choice1[0], choice1[1][0], choice1[1][1]
    country_dict.pop(choice1_country)
    return choice1_country, choice1_city, int(choice1_population)


# ================================================================================
# 5. TIMER FOR MATH GAME
# ================================================================================

time_up = False
exit_thread_event = threading.Event()

def gameTimer(time_per_question = 8):
    """This function starts an 8 second timer. After 8 seconds has elapsed it exits.
    It also exits if it detects that the global 'exit_thread_event' event has been toggled.
    If it has, then it resets the event before terminating its execution.

    Args:
        time_per_question (int, optional): The number of seconds that the timer runs until. Defaults to 8.
    """    
    global time_up
    global exit_thread_event

    start_time = datetime.now()

    while (datetime.now() - start_time).total_seconds() <= time_per_question:
        remaining_time = time_per_question - (datetime.now() - start_time).total_seconds()
        remaining_time = round(remaining_time, 2)

        if exit_thread_event.is_set():
            exit_thread_event.clear() 
            sys.exit()

    clearScreenAfterDelay(0)
    print("TIME UP! Press the enter key to move on.")
    time_up = True
    sys.exit()


# ================================================================================
# 6. MATH GAME
# ================================================================================


def playMathGame():
    """This function plays through the math game for both players. It calls the startMathGame function, 
    providing for each player 1 and player 2, then after stores the returned value as 'player_1_score'
    and 'player_2_score'. It later compares their scores to determine the outcome of the math game - whether
    any player won or if it's a draw - and decrements the global life of the player accordingly. 
    """    
    player_1 = active_users['player1']
    player_2 = active_users['player2']

    print(f"PLAYER 1's turn: {player_1['username']}")
    player_1_score = startMathGame(player_1)
    print(f"PLAYER 2's turn: {player_2['username']}")
    player_2_score = startMathGame(player_2)

    print(f"{player_1['username']}'s Score: {player_1_score}\n{player_2['username']}'s Score: {player_2_score}")

    if player_1_score > player_2_score:
        print(f"{player_1['username']} wins!")
        player_2['global_lives'] -= 1
    elif player_1_score == player_2_score:
        print(f"IT'S A DRAW!")
    else:
        print(f"{player_2['username']} wins!")
        player_1['global_lives'] -= 1

    sleep(3)

def startMathGame(user):
    """Runs the math game until a the player runs out of attempts, after which the function terminates and returns
    the score for the player. 

    The function retrieves the equation and its solution from the generateMathQuestion() function.

    The function starts the gameTimer() function on a separate thread for each question that is asked and upon user input, 
    checks if the global 'time_up' flag is set as True, if it is, then the function runs through the loop again.

    There is also input validation performed within the function, where the user input is checked to be numeric using 
    the is_digit() method and the '-' is stripped from the start of the input to allow the user to input negative numbers 
    without getting a False value from is_digit() for the validation check.

    Comparing the user input with the solution, the function decrements the local lives (attempts) of the player accordingly if they 
    get the answer wrong and awards +10 points if the user input is the correct answer.

    Args:
        user (str): The username of the player currently playing the game.

    Returns:
        int: The final score of the player for the game.
    """    
    global time_up
    global exit_thread_event

    player_score = 0
    player_lives = 3

    while True:
        if not player_lives <= 0:
            clearScreenAfterDelay(1)

            equation, solution = generateMathQuestion()
            timer_thread = threading.Thread(target = gameTimer)

            timer_thread.start()

            user_input = input(f"User Playing: {user['username']}\n\nYOU HAVE 8 SECONDS and {player_lives} attempts:\n\nEnter the answer to:\n\t\t{equation}\n\n\t\tAnswer  :")
            
            if time_up:
                player_lives -= 1
                time_up = False
                continue

            if not user_input.lstrip('-').isdigit():
                player_lives -= 1
                clearScreenAfterDelay(0)
                print('Invalid input, you lose an attempt.')
                exit_thread_event.set()
                continue

            user_input = int(user_input)

            if user_input == solution:
                exit_thread_event.set()
                print('Correct answer.')
                player_score += 10
                clearScreenAfterDelay(1)
            else:
                exit_thread_event.set()
                player_lives -= 1
                print('Wrong answer.')
        else:
            print('OUT OF ATTEMPTS')
            clearScreenAfterDelay(1)
            return player_score
                
def generateMathQuestion():
    """The function randomly chooses between generating one of three different forms of mathematical equations.
    It returns the generated equation along with its solution.
    
    For each type of equation, three different mathematical operators are randomly chosen 
    from the 'math_operators' list. The kind of equation to generate is randomly chosen
    by generating a random integer between 0 and 2 and using match, case statements
    based on the value of the random integer.

    Returns:
        str: The equation that is to be displayed to the user.
        int: The solution to the equation.
    """    
    math_operators = [ [operator.mul, 'x'], [operator.add, '+'], [operator.sub, '-'] ]

    operator1 = random.choice(math_operators)
    operator2 = random.choice(math_operators)

    a = random.randrange(1, 5)
    b = random.randrange(1, 10)
    c = random.randrange(1, 10)

    random_equation_choice = random.randint(0, 2)

    match random_equation_choice:
        case 0:
            equation = f'Equation: ({a} {operator1[1]} {b}) {operator2[1]} {c}'
            solution = operator2[0](operator1[0](a, b), c)
        case 1:
            exponent = random.randrange(1, 4)

            equation = f'Equation: ({a}^({exponent}) {operator2[1]} {b}) {operator1[1]} {c}'
            solution = operator1[0](operator2[0](a**exponent, b), c)
        case 2:
            d = random.randrange(1, 10)
            operator3 = random.choice(math_operators)

            equation = f'Equation: ({a} {operator1[1]} {b}) {operator2[1]} ({c} {operator3[1]} {d})'
            solution = operator2[0](operator1[0](a, b), operator3[0](c, d))
    return equation, solution

def promptUserForGame():
    """This function prompts the user to choose the game that they want to play between 3 different games.
    Based on the user's input, it goes on to execute the function that starts the game that they've chosen to play.

    Returns:
        None: The return statement executes the function respective to the game that the player wants
        to play, and returns it. Hence, as it's executing the function in the return statement, the 
        function returns a None type.
    """    
    clearScreenAfterDelay(0)
    print("╔════════════════════════════════════════════════════════╗")
    print("║ ____            _     _____          _                 ║")
    print("║| __ ) _ __ __ _(_)_ _|_   _| __ __ _(_)_ __   ___ _ __ ║")
    print("║|  _ \| '__/ _` | | '_ \| || '__/ _` | | '_ \ / _ \ '__|║")
    print("║| |_) | | | (_| | | | | | || | | (_| | | | | |  __/ |   ║")
    print("║|____/|_|  \__,_|_|_| |_|_||_|  \__,_|_|_| |_|\___|_|   ║")
    print("╚════════════════════════════════════════════════════════╝")  
    print(f"Player1: elo: ({user_profiles[active_users['player1']['username']]['elo']}) {active_users['player1']['username']}, Remaining Lives: {active_users['player1']['global_lives']}")
    print(f"Player2: elo: ({user_profiles[active_users['player2']['username']]['elo']}) {active_users['player2']['username']}, Remaining Lives: {active_users['player2']['global_lives']}")
    print('\n')
    print('The following games are avaliable:\n')
    print('╒═══════════════════════════════════╕')
    print('│1. Geography Hangman               │')
    print('├───────────────────────────────────┤')
    print('│2. Higher or Lower - Capital Cities│')
    print('├───────────────────────────────────┤')
    print('│3. Quick Maths                     │')
    print('╘═══════════════════════════════════╛')

    print('\n')

    game_choice = input('Choose which game to play: (1 / 2 / 3)')

    if game_choice.isdigit():
        game_choice = int(game_choice)
        if game_choice == 1:
            return P1_P2_hangman()
        elif game_choice == 2:
            return higher_lower()
        elif game_choice == 3:
            return playMathGame() 
        else:
            print('Invalid Input, please try again.')
            sleep(1)
    else:
        print('Invalid Input, please try again.')

if __name__ == "__main__":
    gameplay()
# import PySimpleGUI as sg

def preference_incorporation(profile, schedule):
    return

def generate(profile, hard_requirements):
    return

def operationalize(profile):
    # Training level, 0 - 4 (Beginner, Rookie, Intermediate, Experienced, Advanced).
    training_level = profile[0][4]

    # If time was spent in the gym before, then we count that with the experience.
    schedule_before = 0
    if profile[0][5] == True:
        schedule_before = 1

    # Calculate experience with the given training level * 0.2, and + 1 if they have followed a training schedule
    # before.
    experience = training_level * 0.2 + schedule_before
    
    # Intensity, 0 - 2 (Light, Medium, Heavy).
    intensity = 2
    if experience < 1:
        intensity = 0
    elif experience < 2:
        intensity = 1

    age = profile[0][0]

    # If the client is over the age of 65 or under the age of 16, then the maximum intensity level is
    # medium, for health reasons.
    if intensity > 1 and (age > 65 or age < 16):
        intensity = 1

    hard_requirements = [experience, intensity]
    return hard_requirements

def parse_input(data, preferences, injuries):
    profile = [data, injuries, preferences]
    return profile

def main():
    # sg.change_look_and_feel('Reddit')    # Add a touch of color

    # # All the stuff inside your window.
    # layout = [  
    #     [sg.Text('Please fill in client information and click Ok')],
    #     [sg.Text('Age'), sg.InputText()],
    #     [sg.Text('Gender'), sg.InputCombo(('Male', 'Female'), size=(20, 3))],
    #     [sg.Text('Weight in kg'), sg.InputText()],
    #     [sg.Text('Time available per week in hours'), sg.InputText()],
    #     [sg.Text('Training level (1-5)'), sg.InputText()],
    #     [sg.Checkbox('Client has followed training schedules before')],
        
    #     [sg.Text('Goal'), sg.InputCombo(('Rehabilitation', 'General', 'Weight loss', 'Physical therapy', 'Powerlifting', 
    #                                       'General strength', 'Bodybuilding', 'General aesthetics', 'General endurance', 
    #                                       'Specific endurance'), size=(20, 10))],
    #     [sg.Checkbox('Client has specific preferences')],
    #     [sg.Checkbox('Client has one or more injuries')],
        
    #     [sg.Button('Next'), sg.Button('Cancel')] ]

    # # Create the Window
    # window = sg.Window('Window Title', layout)

    # Data format: [Age, Gender, Weight, Hours, Level, TrainingScheduleFollowed, Goal]
    data = [18, "M", 70, 3, 2, False, "Strength", [None]]

    # List of preferences. Always, in preferences, define exercises to remove from schedule.
    preferences = None

    # List of injuries.
    injuries = ["Back"]

    # # Event Loop to process "events" and get the "values" of the inputs.
    # while True:
    #     event, values = window.read()
    #     if event in (None, 'Cancel'):   # if user closes window or clicks cancel.
    #         break
    #     print(values)
    #     data = values 
        
    #     #if data[7] == True:
        
    #     #if data[8] == True:
            

    # window.close()

    # Parse all input. All information will be stored inside the profile.
    profile = parse_input(data, preferences, injuries)

    # Determine hard component requirements. Format is always [Intensity, Time Spent, Experience].
    hard_requirements = operationalize(profile)

    # Generate a schedule from the set of existing schedules, depending on the profile and hard requirements.
    schedule = generate(profile, hard_requirements)

    # Adapt the schedule to the preferences.
    schedule = preference_incorporation(profile, schedule)

    # Judgment by the client.
    # Open a new window. Show the schedule. Click yes or no. If yes, end. If no, go back to input.

if __name__ == '__main__':
    main()
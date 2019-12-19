import PySimpleGUI as sg
import random, re
from owlready2 import *

# The lists of exercises for all muscle groups.
#ex_chest = ["Bench Press", "Dumbbell Flyes", "Incline Bench Press", "Machine Flyes"]
#ex_back = ["Dumbbell Rows", "Lat Pulldowns", "Machine Rows", "Cable Rows"]
#ex_legs = ["Squats", "Leg Curls", "Leg Extensions", "Romanian Deadlifts", "Prone Leg Curls"]
#ex_biceps = ["Curls", "Hammer Curls", "Reverse Grip Curls"]
#ex_triceps = ["Bar Pushdowns", "Skullcrushers", "Rope Pushdowns"]
#ex_abs = ["Crunches", "Sit-ups", "Bicycle Sit-ups", "Planking"]
#ex_shoulders = ["Military Press", "Lateral Raises", "Face Pulls", "Rear Delt Machine"]

onto = get_ontology("file://./final_ontology2.owl").load() #Can also load after GUI to reduce load time, then move the global variables

#Classes
ex_chest = onto.search(type = onto.ChestExercise)
ex_back = onto.search(type = onto.BackExercise)
ex_legs = onto.search(type = onto.LegsExercise)
ex_biceps = onto.search(type = onto.BicepsExercise)
ex_triceps = onto.search(type = onto.TricepsExercise)
ex_abs = onto.search(type = onto.AbsExercise)
ex_shoulders = onto.search(type = onto.ShouldersExercise)

onto_injuries = onto.search(iri = "*Injury")[1:]
onto_goals = onto.search(subclass_of = onto.Goal)[1:]

def preference_incorporation(profile, schedule):
    return

def generate(profile, hard_requirements, components):
    # Use number of sessions from the profile to determine a schedule. Then divide the muscle
    # groups over the sessions.
    sessions_number = profile.TimeAvailable[0]

    # The experience level will also count.
    experience = hard_requirements[0]

    # The type of schedule the client will follow.
    schedule_type = ""

    # List of sessions. The maximum number of sessions is three. If fewer sessions are used, the other three are
    # empty, usable for later scheduling.
    session = [[], [], []]

    if sessions_number < 2:
        schedule_type = "Full-Body"
    elif sessions_number < 3:
        schedule_type = "Upper-Lower"
    elif sessions_number >= 3:
        if experience < 1:
            schedule_type = "PPL"
        else:
            schedule_type = "Classic-Split"


    # Depending on the schedule type, now divide muscle groups.
    if schedule_type == "Full-Body":
        for muscle_group in components:
            for component in muscle_group:
                session[0].append(component)
    

    elif schedule_type == "Upper-Lower":
        for muscle_group in range(0, 7):
            for component in components[muscle_group]:
                if muscle_group == 0 or muscle_group == 1 or muscle_group == 6 or muscle_group == 3 or muscle_group == 4:
                    session[0].append(component)
                else:
                    session[1].append(component)

    elif schedule_type == "PPL":
        for muscle_group in range(0, 7):
            for component in components[muscle_group]:
                if muscle_group == 0 or muscle_group == 6 or muscle_group == 4:
                    session[0].append(component)
                elif muscle_group == 1 or muscle_group == 3 or muscle_group == 6:
                    session[1].append(component)
                else:
                    session[2].append(component)

    elif schedule_type == "Classic-Split":
        for muscle_group in range(0, 7):
            for component in components[muscle_group]:
                if muscle_group == 0 or muscle_group == 1:
                    session[0].append(component)
                elif muscle_group == 2 or muscle_group == 5:
                    session[1].append(component)
                else:
                    session[2].append(component)


    # Some test prints.
    print(schedule_type)
    print("\n")
    print(session[0])
    print("\n")
    print(session[1])
    print("\n")
    print(session[2])
    print("\n")

    return

def get_exercises(group, generic_exercise_list, exercise_number, injuries):
    # General function for getting exercises for a specific group, based on the number of
    # exercises we want to get.

    # List where all exercises will go.
    exercise_list = []

    # Check per group if the injury is in the list. If not, then pick exercises from that group.
    counter = 0
    skip = False
    for injury in injuries:
        if group in injury.ancestors():
            skip= True
    
    if not skip:
        while counter < exercise_number:
            new_exercise = random.choice(generic_exercise_list)

            if not new_exercise in exercise_list:
                exercise_list.append(new_exercise)
                counter += 1

    return exercise_list

def component_selection(goal,profile,injuries,hard_component_requirements):
    # Use the goal to find exercises.
    goal = goal.name
    
    
    # Get the list of injuries, to exclude any exercise from that category.
    injuries #List of injuries object, get label with .label (which all should have) otherwise .name for class name
    

    # Depending on time available, pick x exercises from any category.
    sessions_available = profile.TimeAvailable[0]
    exercises_per_group = sessions_available

    # The list of exercises per muscle group.
    chest = get_exercises(onto.Chest_Injury, ex_chest, exercises_per_group, injuries)
    back = get_exercises(injuries[2], ex_back, exercises_per_group, injuries)
    legs = get_exercises(injuries[-11], ex_legs, exercises_per_group, injuries)
    biceps = get_exercises(onto.BicepsInjury, ex_biceps, exercises_per_group, injuries)
    triceps = get_exercises(onto.TricepsInjury, ex_triceps, exercises_per_group, injuries)
    absm = get_exercises(onto.Abs_Injury, ex_abs, exercises_per_group, injuries)
    shoulders = get_exercises(onto.ShoulderInjury, ex_shoulders, exercises_per_group, injuries)

    # Return the combined list of all lists of exercises.
    return [chest, back, legs, biceps, triceps, absm, shoulders]

def operationalize(profile):
    # Training level, 0 - 4 (Beginner, Rookie, Intermediate, Experienced, Advanced).
    training_level = profile.TrainingLevel[0]

    # If time was spent in the gym before, then we count that with the experience.
    schedule_before = 0
    if profile.FollowedScheduleBefore[0] == True:
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

    age = profile.Age[0]

    # If the client is over the age of 65 or under the age of 16, then the maximum intensity level is
    # medium, for health reasons.
    if intensity > 1 and (age > 65 or age < 16):
        intensity = 1

    hard_component_requirements = [experience, intensity]
    return hard_component_requirements

def parse_input(data, preferences, injuries):
    try:
        data[3] = int(data[3])
    except:
        raise Exception("Input error: Time available per week should be an integer")   
    
    chosen_goal = data[-1]
    for onto_goal in onto_goals:
        if chosen_goal in onto_goal.label[0]:
            person_goal = onto_goal()
            break

    #Profile       
    profile = onto.Profile()
    profile.Age = [data[0]]
    profile.Gender = [data[1]]
    profile.Weight = [data[2]]
    profile.TimeAvailable = [data[3]]
    profile.TrainingLevel = [data[4]]
    profile.FollowedScheduleBefore = [data[5]]

    person = onto.Person() #Can give a name
    person.WantsToAchieve = [person_goal]
    person.HasProfile = [profile]

    #Injuries
    #ankle_injury = injuries[0]()
    specified_onto_injuries = []
    for specified_injury in injuries:
        for onto_injury in onto_injuries:
            #re.sub(r'_', "", injuries[-1].name).lower()
            if specified_injury in onto_injury.name:
                specified_onto_injuries.append( onto_injury() )
                break
    person.HasInjury = specified_onto_injuries  #[ankle_injury]

    #Preferences
    pref = onto.Preference()
    pref.HasPreferenceExercise = [onto.Crunches] #A instance here
    pref.ifohasActivityIntensity = [onto.MediumIntensity()] #Can allow Heavy intensity?
    pref.WantsItOrnot = [False]

    pref2 = onto.Preference()
    pref2.HasPreferenceExercise = [onto.ChestExercise("Chest")]  # A class here
    pref2.ifohasActivityIntensity = [onto.HeavyIntensity()]  # Also includes Medium and light to avoid basically
    pref2.WantsItOrnot = [False]

    person.HasPreference = [pref,pref2]

    return person_info = person

def get_data():
    data = None
    preferences = None
    injuries = None
    
    sg.change_look_and_feel('Reddit')    # Add a touch of color
    # All the stuff inside your window.
    layout = [  
        [sg.Text('Please fill in client information and click Next')],
        [sg.Text('Age'), sg.InputText()],
        [sg.Text('Gender'), sg.InputCombo(('M', 'F'), size=(20, 3))],
        [sg.Text('Weight in kg'), sg.InputText()],
        [sg.Text('Time available per week in hours'), sg.InputText()],
        [sg.Text('Training level (1-5)'), sg.Slider(range=(1, 5), orientation='h', size=(10, 20), default_value=1)],
        [sg.Checkbox('Client has followed training schedules before')],
        
        [sg.Text('Goal'), sg.InputCombo(('Rehabilitation', 'General', 'Weight loss', 'Physical therapy', 'Powerlifting', 
                                          'General strength', 'Bodybuilding', 'General aesthetics', 'General endurance', 
                                          'Specific endurance'), size=(20, 10))],
        [sg.Checkbox('Client has specific preferences')],
        
        [sg.Button('Next'), sg.Button('Cancel')] ]
    
    # Create the Window
    window = sg.Window('Create schedule', layout)
    
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):   # if user closes window or clicks cancel
            break
        data = values 
        
        window.close()
        
    if data[7] == True:
        layout = [  
        [sg.Text('Please fill in preferences and click Next')],
        
        [sg.Button('Next'), sg.Button('Cancel')] ]
        
        window = sg.Window('Preferences', layout)
        
        while True:
            event, values = window.read()
            if event in (None, 'Cancel'):   # if user closes window or clicks cancel
                break
            preferences = values 
            
            window.close()
    
    
    layout = [  
    [sg.Text('Please check where the client has an injury and click Next')],
    [sg.Text('Injury 1'), sg.InputCombo(('None', 'Chest', 'Back', 'Legs', 'Biceps', 'Triceps', 
                                      'Abs', 'Shoulders'), default_value='None', size=(20, 7))],
    [sg.Text('Injury 2'), sg.InputCombo(('None', 'Chest', 'Back', 'Legs', 'Biceps', 'Triceps', 
                                      'Abs', 'Shoulders'), default_value='None', size=(20, 7))],
    [sg.Text('Injury 3'), sg.InputCombo(('None', 'Chest', 'Back', 'Legs', 'Biceps', 'Triceps', 
                                      'Abs', 'Shoulders'), default_value='None', size=(20, 7))],
    
    [sg.Button('Next'), sg.Button('Cancel')] ]
    
    window = sg.Window('Injuries', layout)
    
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):   # if user closes window or clicks cancel
            break
        values = list(values.values())
        injuries = [x for x in values if x != 'None']
    
        window.close()
            
    data = list(data.values())[:7]
    
    return data, preferences, injuries

def main():
    
    data, preferences, injuries = get_data()
    # TEST INPUTS BELOW, this is how the data should look once received from the input:

    # Data format: [Age, Gender, Weight, Hours, Level, TrainingScheduleFollowed, Goal]
    #data = [18, "M", 70, 3, 5, False, "Strength"]

    # List of preferences. Always, in preferences, define exercises to remove from schedule.
    preferences = []

    # List of injuries.
    #injuries = []

    # Parse all input. All information will be stored inside the profile.
    person_info = parse_input(data, preferences, injuries)
    profile = person_info.HasProfile[0]
    preferences = person_info.HasPreference
    goal = person_info.WantsToAchieve[0]
    injuries = person.HasInjury
    
    # Determine hard component requirements. Format is always [Intensity, Experience].
    hard_component_requirements = operationalize(profile)

    # Select the components, which in this case include all exercise to be done by the client. In case of an injury,
    # the list of exercises for that specific muscle group is empty. The general format for the exercises
    # list is as follows: [chest, back, legs, biceps, triceps, abs, shoulders].
    components = component_selection(goal,profile,injuries,hard_component_requirements)

    # Generate a schedule from the set of existing schedules, depending on the profile and hard requirements.
    schedule = generate(profile, hard_requirements, components)

    # Adapt the schedule to the preferences.
    schedule = preference_incorporation(profile, schedule)

    # Judgment by the client.
    # Open a new window. Show the schedule. Click yes or no. If yes, end. If no, go back to input.

if __name__ == '__main__':
    main()
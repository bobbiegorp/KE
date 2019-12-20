import PySimpleGUI as sg
import random, re
from owlready2 import *
import math

# Can also load after GUI to reduce waiting time, then move the global variables.
onto = get_ontology("file://./final_ontology2.owl").load()

'''
#General Classes
ex_chest = onto.search(type = onto.ChestExercise)
ex_back = onto.search(type = onto.BackExercise)
ex_legs = onto.search(type = onto.LegsExercise)
ex_biceps = onto.search(type = onto.BicepsExercise)
ex_triceps = onto.search(type = onto.TricepsExercise)
ex_abs = onto.search(type = onto.AbsExercise)
ex_shoulders = onto.search(type = onto.ShouldersExercise)
ex_endurance = onto.search(type = onto.Endurance_Exercise)
'''

onto_injuries = onto.search(iri = "*Injury")[1:]
onto_goals = onto.search(type = onto.Goal)
instan_ex = onto.search(type = onto.Exercise)

def preference_incorporation(preferences, sessions,intensity,components):
    
    #intensity = schedule[1]
    #final_intensities = [intensity]
    
    for pref in preferences:
        
        specified_ex_pref = pref.HasPreferenceExercise[0]
        specified_intensity = pref.ActivityIntensity[0]
        wants_included = pref.WantsItOrnot[0]
        ex_class = specified_ex_pref.is_a[0].label[0]
        
        if not wants_included:
            done = False
            for i,session in enumerate(sessions):
                if done:
                    break
             
                for j,ex in enumerate(session):
                    if ex.name == specified_ex_pref.name:
                        subs_avail = False
                        for muscle_group in components:
                            if len(muscle_group) > 0 and muscle_group[0].is_a[0].label[0] == ex_class:
                                component = muscle_group.pop(0)
                                component.ActivityIntensity = [intensity]
                                sessions[i][j] = component
                                subs_avail = True
                                break
                                
                        if not subs_avail:
                            del sessions[i][j]
                        done = True
                        break
            
        elif specified_intensity <= intensity:
            
            found_session = None
            done = False
            for i,session in enumerate(sessions):
                if done:
                    break
             
                for j,ex in enumerate(session):
                    if ex.name == specified_ex_pref.name:
                        #specification = ("Session %d" % i, ex.name, specified_intensity)
                        #final_intensity.append(specification)
                        already_exists = True
                        ex.ActivityIntensity = [int(specified_intensity)]
                        done = True 
                        break
                        
                    if ex.is_a[0].label[0] == ex_class:
                        found_session = i
            if not already_exists:
                specified_ex_pref.ActivityIntensity = [int(specified_intensity)]
                sessions.append(specified_ex_pref)
                #specification = ("Session %d" % i, specified_ex_pref.name, specified_intensity)
                #final_intensity.append(specification)      
                         
    return sessions #,final_intensities]

def generate(hard_plan_requirements, hard_component_requirements, components):
    # Use number of sessions from the profile to determine a schedule. Then divide the muscle
    # groups over the sessions.
    sessions_amount = min(hard_plan_requirements,3) #3 is max for implementation

    # The experience level will also count.
    intensity = hard_component_requirements[0]
    experience = hard_component_requirements[1]

    # The type of schedule the client will follow.
    schedule_type = ""

    # List of sessions. The maximum number of sessions is three. If fewer sessions are used, the other three are
    # empty, usable for later scheduling.
    session = [[], [], []]

    if sessions_amount < 2:
        schedule_type = "Full-Body"
    elif sessions_amount < 3:
        schedule_type = "Upper-Lower"
    elif sessions_amount >= 3:
        if experience < 1:
            schedule_type = "PPL"
        else:
            schedule_type = "Classic-Split"

    # Depending on the schedule type, now divide the muscle groups.
    # For full body, we simply put all exercises in the first session.
    if schedule_type == "Full-Body":
        for muscle_group in components:
            component = muscle_group.pop(0)
            component.ActivityIntensity = [intensity]
            session[0].append(component)
    
    # For upper-lower split, we put all upper body exercises in the first session, and all other exercises
    # in the second session.
    elif schedule_type == "Upper-Lower":
        for muscle_group in components:
            label = muscle_group[0].is_a[0].label[0]  #class Label
            condition = "Chest" in label or "Shoulders" in label or "Biceps" in label or "Triceps" in label or "Back" in label
            for i in range(2):
                if len(muscle_group) == 0:
                    break
                component = muscle_group.pop(0)
                component.ActivityIntensity = [intensity]
                if condition:
                    session[0].append(component)
                else:
                    session[1].append(component)

    # For PPL and the Classic Split, we divide the muscle groups over the three sessions.
    elif schedule_type == "PPL":
        for muscle_group in components:
            label = muscle_group[0].is_a[0].label[0]  #class Label
            condition = "Chest" in label or "Shoulders" in label or "Triceps" in label
            condition2 = "Abs" in label or "Biceps" in label or "Back" in label

            for i in range(3):
                if len(muscle_group) == 0:
                    break
                component = muscle_group.pop(0)
                component.ActivityIntensity = [intensity]
                if condition:
                    session[0].append(component)
                elif condition2:
                    session[1].append(component)
                else:
                    session[2].append(component)

    elif schedule_type == "Classic-Split":
        for muscle_group in components:
            label = muscle_group[0].is_a[0].label[0]  #class Label
            condition = "Chest" in label or "Back" in label
            condition2 = "Abs" in label or "Legs" in label or "Endurance" in label 
            for i in range(3):
                if len(muscle_group) == 0:
                    break
                component = muscle_group.pop(0)
                component.ActivityIntensity = [intensity]
                if condition:
                    session[0].append(component)
                elif condition2:
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

    return session,components

def check_type_injury(type_injury, generic_exercise_list, injuries):
    # General function for getting exercises for a specific group, based on the number of
    # exercises we want to get.

    # Check per group if the injury is in the list. If not, then return exercises from that group.
    for injury in injuries:
        if type_injury in injury.is_a[0].ancestors():
            return []
            
    return generic_exercise_list

def component_selection(goal,profile,injuries,hard_component_requirements):
    # Use the goal to find exercises.
    goal_instance = goal.name
    goal_class = [ancestor.name for ancestor in goal.is_a[0].ancestors() if ancestor.name != "Thing" and ancestor.name != "Goal"][0]

    # The list of exercises per muscle group if not in injury
    
    #Classes with specific ordering
    ex_chest = [onto.BenchPress, onto.DumbbellFlyes, onto.InclineBenchPress, onto.MachinePress]
    ex_back = [onto.Deadlifts, onto.LateralPulldowns, onto.DumbbellRows, onto.MachineRows, onto.CableRows]
    ex_legs = [onto.Squats, onto.RomanianDeadlifts, onto.LegCurls, onto.LegExtensions, onto.ProneLegCurls]
    ex_biceps = [onto.Curls, onto.HammerCurls, onto.ReverseGripCurls]
    ex_triceps = [onto.BarPushdowns, onto.RopePushdowns, onto.Skullcrushers]
    ex_abs = [onto.Crunches, onto.Situps, onto.Bicycle_Situps, onto.Planking]
    ex_shoulders = [onto.MilitaryPress, onto.LateralRaises, onto.FacePulls, onto.RearDeltMachine]
    ex_endurance = [onto.Running, onto.Cycling, onto.Rowing, onto.Circuit_Training]
    
    chest = check_type_injury(onto.Chest_Injury, ex_chest, injuries)
    back = check_type_injury(onto_injuries[2], ex_back, injuries)
    legs = check_type_injury(onto_injuries[-11], ex_legs, injuries)
    biceps = check_type_injury(onto.BicepsInjury, ex_biceps, injuries)
    triceps = check_type_injury(onto.TricepsInjury, ex_triceps, injuries)
    absm = check_type_injury(onto.Abs_Injury, ex_abs, injuries)
    shoulders = check_type_injury(onto.ShoulderInjury, ex_shoulders, injuries)
    endurance = check_type_injury(onto_injuries[-11], ex_endurance, injuries)
    running_only = [onto.Running] if len(endurance) > 0 else []

    # Return the combined list of all lists of exercises.

    if goal_class == "Endurance":
        components = [endurance]
    elif goal_class == "Health":
        components = [chest,back,legs,absm,shoulders, running_only]
    else:
        components = [chest, back, legs, biceps, triceps, absm, shoulders]
        
    final_components = []
    for list_ex in components:
        if len(list_ex) > 0:
            final_components.append(list_ex)

    # Return the combined list of all lists of exercises.
    return final_components

def operationalize(profile):
    # Training level, 0 - 4 (Beginner, Rookie, Intermediate, Experienced, Advanced).
    training_level = profile.TrainingLevel[0]
    time_spent = profile.TimeSpentGym[0]  

    # If time was spent in the gym before, then we count that with the experience.
    schedule_before = 0
    if profile.FollowedScheduleBefore[0] == True:
        schedule_before = 1

    # Calculate experience with the given training level * 0.2, and + 1 if they have followed a training schedule
    # before.
    for i in range(1,6):
        thresh = i * 20 
        if min(time_spent,99) < thresh:
            time_spent_addition = i * 0.2
            break
    
    experience = training_level * 0.2 + schedule_before + time_spent_addition  
    
    # Intensity, 0 - 2 (Light, Medium, Heavy).
    intensity = 3
    if experience < 1:
        intensity = 1
    elif experience < 2:
        intensity = 2

    age = profile.Age[0]

    # If the client is over the age of 65 or under the age of 16, then the maximum intensity level is
    # medium, for health reasons.
    if intensity > 2 and (age > 60 or age < 16):
        intensity = 2

    hard_component_requirements = [intensity,experience]
    return hard_component_requirements

def parse_input(data, preferences, injuries):
    # Checks for the data that was in the input, if their types were correct.
    try:
        data[0] = int(data[0])
    except:
        raise Exception("Input error: Age should be an integer")
        
    try:
        data[2] = int(data[2])
    except:
        raise Exception("Input error: Weight should be an integer")
    
    try:
        data[3] = int(data[3])
    except:
        raise Exception("Input error: Time available per week should be an integer")  
        
    try:
        data[7] = int(data[7])
    except:
        raise Exception("Input error: Estimated total time spent in gym should be an integer")  
    
        
    print(data[6])
    chosen_goal = data[6].lower().replace(" ","")
    for onto_goal in onto_goals:
        base_goal_name = re.sub(r'_', "", onto_goal.name).lower() #Do this in case of exercises with a _ seperator
        if chosen_goal == base_goal_name:
            person_goal = onto_goal
            break

    # Profile       
    profile = onto.Profile()
    profile.Age = [data[0]]
    profile.Gender = [data[1]]
    profile.Weight = [data[2]]
    profile.TimeAvailable = [data[3]]
    profile.TrainingLevel = [data[4]]
    profile.FollowedScheduleBefore = [data[5]]
    profile.TimeSpentGym = [data[7]] #<----------------------------------------------------------------Uncomment this if implemented

    person = onto.Person() #Can give a name
    person.WantsToAchieve = [person_goal]
    person.HasProfile = [profile]

    # Parse the injury inputs.
    #ankle_injury = injuries[0]()
    specified_onto_injuries = []
    for specified_injury in injuries:
        for onto_injury in onto_injuries:
            if specified_injury == onto_injury.label[0]:
                specified_onto_injuries.append( onto_injury() )
                break
    person.HasInjury = specified_onto_injuries  #[ankle_injury]

    # Parse the preferences.
    specified_ont_preferences = []
    if type(preferences) != list:
        preferences = []
        
    for specified_preference in preferences:
        specified_onto_ex = None
        
        for onto_ex in instan_ex:
            # base_name = re.sub(r'_', "", onto_ex.name).lower() #Do this in case of exercises with a _ seperator
            # specified_preference_ex = specified_preference[0].lower()
            if specified_preference[0] == onto_ex.name: #in base_name:
                specified_onto_ex = onto_ex
                break

        pref = onto.Preference()
        pref.HasPreferenceExercise = [specified_onto_ex]
        pref.ActivityIntensity = [specified_preference[1]]
        pref.WantsItOrnot = [specified_preference[2]]
        specified_ont_preferences.append(pref)

    person.HasPreference = specified_ont_preferences

    return person

def get_data():
    data = None
    preferences = None
    injuries = None
    
    # Add a touch of color.
    sg.change_look_and_feel('Reddit')
    
    # All the stuff inside the UI window.
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
        [sg.Text('Estimated total time spent in gym in hours'), sg.InputText()],
        
        [sg.Button('Next'), sg.Button('Cancel')] ]
    
    # Create the Window
    window = sg.Window('Create schedule', layout)
    
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):   # if user closes window or clicks cancel
            if event == 'Cancel':
                window.close()
                return [], [], []
            break
        
        data = values 
        
        window.close()
      
    # Preference incorporation in the input.
    if data[7] == True:
        #possible_values = ex_abs + ex_back + ex_biceps + ex_chest + ex_legs + ex_shoulders + ex_triceps
        possible_values = [ex.name for ex in onto.search(type = onto.Exercise)]
        
        layout = [  
        [sg.Text('Please fill in preferences and click Next')],
        [sg.Text('                                                                       '), 
         sg.Text('Intensity')],
        
        [sg.Text('Preference 1'), sg.InputCombo(possible_values, default_value='None', size=(20, 7)),  
         sg.Text('    '),
         sg.Slider(range=(1, 3), orientation='h', size=(10, 20), default_value=1),
         sg.Text('    '),
         sg.Checkbox('Include')],
        
        [sg.Text('Preference 2'), sg.InputCombo(possible_values, default_value='None', size=(20, 7)),  
         sg.Text('    '),
         sg.Slider(range=(1, 5), orientation='h', size=(10, 20), default_value=1),
         sg.Text('    '),
         sg.Checkbox('Include')],
        
        [sg.Text('Preference 3'), sg.InputCombo(possible_values, default_value='None', size=(20, 7)),  
         sg.Text('    '),
         sg.Slider(range=(1, 5), orientation='h', size=(10, 20), default_value=1),
         sg.Text('    '),
         sg.Checkbox('Include')],
        
        [sg.Button('Next'), sg.Button('Cancel')] ]
        
        window = sg.Window('Preferences', layout)
        
        while True:
            event, values = window.read()

            # If the user closes window or clicks cancel.
            if event in (None, 'Cancel'):
                if event == 'Cancel':
                    window.close()
                    return [], [], []
                break

            # Create right output data shape.          
            values = list(values.values())
            new_values = []
            for i in range(len(values)):
                first_index = math.floor(i / 3)
                modulo = i % 3
                if modulo == 0:
                    if values[i] == '':
                        break
                    new_values.append([])
                new_values[first_index].append(values[i])
                
            preferences = new_values
            
            print(preferences)
            
            window.close()
    
    #possible_injuries = ['None', 'Chest', 'Back', 'Legs', 'Biceps', 'Triceps', 
    #                                  'Abs', 'Shoulders']
    
    possible_injuries = [ x.label[0] for x in onto.search(iri = "*Injury")[1:] if x.name != "Injury" and x.name != 'Connective_and_Soft_Tissue_Injury']
    
    layout = [  
    [sg.Text('Please check where the client has an injury and click Next')],
    [sg.Text('Injury 1'), sg.InputCombo(possible_injuries, default_value='None', size=(20, 7))],
    [sg.Text('Injury 2'), sg.InputCombo(possible_injuries, default_value='None', size=(20, 7))],
    [sg.Text('Injury 3'), sg.InputCombo(possible_injuries, default_value='None', size=(20, 7))],
    
    [sg.Button('Next'), sg.Button('Cancel')] ]
    
    window = sg.Window('Injuries', layout)
    
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):   # if user closes window or clicks cancel
            if event == 'Cancel':
                window.close()
                return [], [], []
            break
        values = list(values.values())
        injuries = [x for x in values if x != 'None']
    
        window.close()
            
    data = list(data.values())
    del data[7]
    
    return data, preferences, injuries


def subfunct_text(schedule, i, j):
    try:
        string = str(schedule[j][i].name) + " " + str(schedule[j][i].ActivityIntensity)
        return sg.Text(string.ljust(20), size=(20,1))
    except:
        return sg.Text(' '.ljust(20), size=(20,1))

def get_approval(schedule):

    #final_intensities = schedule[1]
    #schedule = schedule[0]

    # Set the standard value of approved to True.
    approved = True
    
    headings = ['Session ' + str(i+1) for i in range(3) if schedule[i]]
    header =  [[sg.Text('  ')] + [sg.Text(h, size=(20,1)) for h in headings]]

    max_exer = 0
    for sess in schedule:
        if len(sess) > max_exer:
            max_exer = len(sess)
    
    input_rows = [[subfunct_text(schedule, i, j) for j in range(len(headings))] for i in range(max_exer)]

    layout = header + input_rows + [[sg.Button('Refuse')]]
    
    window = sg.Window('Schedule approval', layout)
    
    # Wait for the scheduler to input whether or not the schedule was refused or not.
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):   # if user closes window or clicks cancel
            if event == 'Cancel':
                window.close()
                return None
            break
        
        if event == 'Refuse':
            approved = False
            window.close()
            break
    
    return approved
    

def main():
    
    data, preferences, injuries = get_data()
    if data == [] and preferences ==  [] and injuries == []:
        return None
    # TEST INPUTS BELOW, this is how the data should look once received from the input:

    # Data format: [Age, Gender, Weight, Hours, Level, TrainingScheduleFollowed, Goal]
    #data = [18, "M", 70, 3, 5, False, "General strength"]

    # List of preferences. Always, in preferences, define exercises to remove from schedule.
    #crunches = instan_ex[0].name
    #circuit = instan_ex[15].name #If used for first time
    #preferences = [ [instan_ex[0].name,2,False],[circuit,1,False] ]
    #preferences = []

    # List of injuries.
    #back_injury = onto_injuries[2].label[0]
    #injuries = [ back_injury ] #Backinjury
    #injuries = []

    # Parse all input. All information will be stored inside the profile.
    person_info = parse_input(data, preferences, injuries)
    profile = person_info.HasProfile[0]
    preferences = person_info.HasPreference
    goal = person_info.WantsToAchieve[0]
    injuries = person_info.HasInjury
    
    #profile.TimeSpentGym = [41] #-----------------------------------------------------------------------Remove this if implemented
    print(preferences)
    print(profile.TimeSpentGym)
    
    # Determine hard component requirements. Format is always [Intensity, Experience].
    hard_component_requirements = operationalize(profile)
    intensity = hard_component_requirements[0]

    # Select the components, which in this case include all exercise to be done by the client. In case of an injury,
    # the list of exercises for that specific muscle group is empty. The general format for the exercises
    # list is as follows: [chest, back, legs, biceps, triceps, abs, shoulders].
    components = component_selection(goal,profile,injuries,hard_component_requirements)
    #print(components,"\n")
    # Generate a schedule from the set of existing schedules, depending on the profile and hard requirements.
    hard_plan_requirements = profile.TimeAvailable[0]
    schedule,components = generate(hard_plan_requirements, hard_component_requirements, components)
   
    for s in schedule:
        for ex in s:
            print(ex.name,ex.ActivityIntensity)

    # Adapt the schedule to the preferences.
    schedule = preference_incorporation(preferences, schedule,intensity,components)
    
    session = schedule
    print("After preference incorporation")
    print("\n")
    print(session[0])
    print("\n")
    print(session[1])
    print("\n")
    print(session[2])
    print("\n")
    for s in session:
        for ex in s:
            print(ex.name,ex.ActivityIntensity)
    #return
    # Judgment by the client.
    # Open a new window. Show the schedule. Click yes or no. If yes, end. If no, go back to input.
    approved = get_approval(schedule)
    
    if approved is None:
        return None
    
    if not approved:
        schedule = main()
        
    return schedule

if __name__ == '__main__':
    main()

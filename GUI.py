import PySimpleGUI as sg

sg.change_look_and_feel('Reddit')    # Add a touch of color
# All the stuff inside your window.
layout = [  
    [sg.Text('Please fill in client information and click Ok')],
    [sg.Text('Age'), sg.InputText()],
    [sg.Text('Gender'), sg.InputCombo(('Male', 'Female'), size=(20, 3))],
    [sg.Text('Weight in kg'), sg.InputText()],
    [sg.Text('Time available per week in hours'), sg.InputText()],
    [sg.Text('Training level (1-5)'), sg.InputText()],
    [sg.Checkbox('Client has followed training schedules before')],
    
    [sg.Text('Goal'), sg.InputCombo(('Rehabilitation', 'General', 'Weight loss', 'Physical therapy', 'Powerlifting', 
                                      'General strength', 'Bodybuilding', 'General aesthetics', 'General endurance', 
                                      'Specific endurance'), size=(20, 10))],
    [sg.Checkbox('Client has specific preferences')],
    [sg.Checkbox('Client has one or more injuries')],
    
    [sg.Button('Next'), sg.Button('Cancel')] ]

# Create the Window
window = sg.Window('Window Title', layout)
data = None
preferences = None
injuries = None

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in (None, 'Cancel'):   # if user closes window or clicks cancel
        break
    print(values)
    data = values 
    
    #if data[7] == True:
    
    #if data[8] == True:
        

window.close()
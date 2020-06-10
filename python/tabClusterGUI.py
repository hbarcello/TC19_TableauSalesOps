import cluster_engine
import PySimpleGUI as sg
import pandas as pd

sg.theme('DarkAmber')	# Add a touch of color
# All the stuff inside your window.
layout = [  [sg.Text('Tableau Clustering Tool')], [sg.In("Browse For Input File Location(CSV)..."), sg.FileBrowse()],
            [sg.In("Browse For Output File Location..."), sg.SaveAs()],
            [sg.Button('Ok'), sg.Button('Validate'), sg.Button('Exit')],
            [sg.ProgressBar(200, orientation='h', size=(20, 20), key='progbar'),
             sg.Text("Clustering Progress", key='cpg')]
            ]

# Create the Window
window = sg.Window('Territory Clustering', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in (None, 'Exit'):	# if user closes window or clicks cancel
        break
    if event == 'Validate' and len(values[0]) > 0:
        newdf = pd.read_csv(values[0])
        pop_up_string = newdf.dtypes
        sg.popup(pop_up_string)
        # Should work but doesn't clustering.cluster_generator(values[0])
    if event == 'Ok' and len(values[0]) > 0:
        progress_bar = window.FindElement('progbar')
        progress_text = window.FindElement('cpg')
        progress_text("Loading Input")
        progress_bar.update_bar(1,3)
        input_data = pd.read_csv(values[0])
        progress_bar.update_bar(2,3)
        progress_text("Clustering + Writing File Output")
        cluster_engine.cluster_writer(cluster_engine.cluster_generator(input_data), str(values[1]) + ".xlsx")
        progress_bar.update_bar(3,3)
        progress_text("Done!")

window.close()



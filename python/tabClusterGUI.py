############################
# By Hunter Barcello       #
# Last Update : 8-2-2024   #
# hbarcello@gmail.com      #
#######################################################################
# Note : PySimpleGUI needs some additional work to run on Mac Silicon #
# For the moment, only command line interface is supported on the ARM #
# (M1, M2, etc)                                                       #
#######################################################################

import cluster_engine
import FreeSimpleGUI as sg
import pandas as pd

sg.theme('DarkAmber')  # Add a touch of color
# All the stuff inside your window.
layout = [[sg.Text('Tableau Clustering Tool')], [sg.In("Browse For Input File Location(CSV)..."), sg.FileBrowse()],
          [sg.In("Browse For Output File Location..."), sg.SaveAs()],
          [sg.Text("Desired Clusters Per Territory: "), sg.Slider(range=(5, 30), default_value=10, size=(15, 20),
                                                                  orientation='horizontal')],
          [sg.Button('Ok'), sg.Button('Validate'), sg.Button('Exit')],
          [sg.ProgressBar(200, orientation='h', size=(20, 20), key='progbar'),
           sg.Text("Clustering Progress", key='cpg')],
          [sg.Text("Created by Hunter Barcello : hbarcello@gmail.com", font='Helvetica, 7')]
          ]

# Create the Window
window = sg.Window('Territory Clustering', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in (None, 'Exit'):  # if user closes window or clicks cancel
        break
    if event == 'Validate' and len(values[0]) > 0:
        newdf = pd.read_csv(values[0])
        pop_up_string = newdf.dtypes
        sg.popup(pop_up_string)
        # Should work but doesn't  -- clustering.cluster_generator(values[0])
    if event == 'Ok' and len(values[0]) > 0:
        progress_bar = window['progbar']
        progress_text = window['cpg']
        progress_text("Loading Input")
        progress_bar.update_bar(1, 3)
        input_data = pd.read_csv(values[0])
        progress_bar.update_bar(2, 3)
        progress_text("Clustering + Writing File Output")
        cluster_engine.cluster_writer(cluster_engine.cluster_generator(input_data, cluster_factor=int(values[2])),
                                      str(values[1]) + ".xlsx")
        progress_bar.update_bar(3, 3)
        progress_text("Done!")

window.close()

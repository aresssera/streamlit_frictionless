import streamlit as st
import time
import json
import os
from frictionless import validate
from frictionless import Schema
from mapping import ogdNbr_mapping
from urllib.request import urlopen
import pandas as pd

# function to perform quality check
def perform_quality_check(frame, file_name):

    MAX_RETRIES = 2
    DELAY_SECONDS = 1

    try:

        if file_name in ogdNbr_mapping:
            ID = ogdNbr_mapping[file_name]
            datapackage_url = f"https://www.uvek-gis.admin.ch/BFE/ogd/{ID}/datapackage.json"
            url_ogd = 'https://www.uvek-gis.admin.ch/BFE/ogd/'

            st.write(file_name)
           

            # fetching datapackage with retry logic
            attempts = 0
            while attempts < MAX_RETRIES:
                try:
                    response = urlopen(datapackage_url)
                    st.write(response.getcode())
                    
                    if response.getcode() == 200:
                        datapackage = response.read().decode('utf-8')
                        st.write('INSIDE IF ')
                        datapackage_json = json.loads(datapackage)
                        

                        # change source file
                        jsonAsString = str(datapackage_json)
                        st.write(jsonAsString)
                        st.write('99999999999999999999999999')


                        # fehler hier
                        folderPath = url_ogd + ID + '/'
                        st.write(os.path.join(folderPath, file_name))
                        st.write('88888888888888888888888888888888')
                        jsonAsString = jsonAsString.replace(os.path.join(folderPath, file_name), file_name)
                        st.write(jsonAsString)
                        st.write('77777777777777777777777777777777777777777')
                        # fehler hier

                        st.write(jsonAsString)
                        st.write('666666666666666666666666666666666666666')
                        updatedJSON = ast.literal_eval(jsonAsString)

                        st.write(updatedJSON)
                        
                        if updatedJSON:

                            # perform validation using schema matched to uploaded file
                            report = validate(updatedJSON)
                            
                            return report

                        return f"No schema found for the uploaded file '{file_name}' in the datapackage."

                except Exception as e:
                    print(f"Error fetching datapackage: {e}")

                attempts += 1
                # exponential backoff delay
                time.sleep(DELAY_SECONDS * attempts)  

            return f"Failed to fetch datapackage after multiple attempts."

        else:
            return f"There is no datapackage for the file '{file_name}' "

    except Exception as e:
        return f"Error during validation: {e}"


# get cleaner error messages
def get_error_messages(report):

    text = ''
    
    for err in report.tasks[0].errors:
        text = text + err.title + ':\n' + err.message + '\n\n'

    return text


#-------------------------------------------------------------------------------
# translation dictionaries
translations = {
    "Deutsch": {
        "title": "CSV-Qualitätsprüfung mit Frictionless",
        "upload": "Laden Sie eine CSV-Datei hoch",
        "uploaded_success": "Datei erfolgreich hochgeladen!",
        "check_button": "Überprüfen",
        "error": "Fehler während der Validierung:",
        "validation_complete": "Validierung abgeschlossen!",
        "valid": "Das Dokument ist gültig.",
    },
    "Français": {
        "title": "Contrôle de qualité CSV avec Frictionless",
        "upload": "Télécharger un fichier CSV",
        "uploaded_success": "Fichier téléchargé avec succès !",
        "check_button": "Vérifier",
        "error": "Erreur de validation:",
        "validation_complete": "Validation terminée !",
        "valid": "Le document est valide.",
    },
    "Italiano": {
        "title": "Controllo qualità CSV con Frictionless",
        "upload": "Caricare un file CSV",
        "uploaded_success": "File caricato con successo!",
        "check_button": "Controllo",
        "error": "Errore durante la validazione:",
        "validation_complete": "Validazione completata!",
        "valid": "Il documento è valido.",
    },
    "English": {
        "title": "CSV Quality Check with Frictionless",
        "upload": "Upload a CSV file",
        "uploaded_success": "File uploaded successfully!",
        "check_button": "Check",
        "error": "Error during validation:",
        "validation_complete": "Validation complete!",
        "valid": "The document is valid.",
    }
}
#-------------------------------------------------------------------------------

# function for changing language
def set_language(language):
    st.session_state.language = language

# main function
def main():
    # default language German
    if "language" not in st.session_state:
        st.session_state.language = "Deutsch"

    # language selection dropdown
    selected_language = st.sidebar.selectbox("Select Language", list(translations.keys()), index=list(translations.keys()).index(st.session_state.language))
    set_language(selected_language)

    # display content based on selected language
    translation = translations[st.session_state.language]

    st.title(translation["title"])

    uploaded_file = st.file_uploader(translation["upload"], type=["csv"])

    if uploaded_file is not None:
        st.write(translation["uploaded_success"])

       
            
        # display content of CSV
        dataframe = pd.read_csv(uploaded_file, sep='[;,]', engine='python', skip_blank_lines=False)
        st.write(dataframe)

         # save file name
        file_name = uploaded_file.name
        
        with open(uploaded_file.name, 'wb') as f:
            f.write(uploaded_file.read())

        # whenn button is pressed
        if st.button(translation["check_button"]):
            progress_bar = st.progress(0)
            report = perform_quality_check(f, file_name)

            if isinstance(report, str):
                st.error(f"{translation['error']} {report}")
            else:
                if report.valid:
                    st.success(translation["validation_complete"])
                    st.success(translation["valid"])
                else:
                    st.error(translation["validation_complete"])
                    st.error(get_error_messages(report))

if __name__ == "__main__":
    main()

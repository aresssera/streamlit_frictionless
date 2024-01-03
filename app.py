import streamlit as st
import time
import json
from frictionless import validate
from frictionless import Schema
from mapping import ogdNbr_mapping
from urllib.request import urlopen

# function to perform quality check
def perform_quality_check(file):

    MAX_RETRIES = 2
    DELAY_SECONDS = 1

    try:
        file_name = file.name

        # save uploaded file locally
        with open(file_name, 'wb') as f:
            f.write(file.read())

        # load the local file path
        local_file_path = file_name  # Update this to your file path

        if file_name in ogdNbr_mapping:
            ID = ogdNbr_mapping[file_name]
            datapackage_url = f"https://www.uvek-gis.admin.ch/BFE/ogd/{ID}/datapackage.json"

            # fetching datapackage with retry logic
            attempts = 0
            while attempts < MAX_RETRIES:
                try:
                    #print(datapackage_url)
                    response = urlopen(datapackage_url)
                    
                    if response.getcode() == 200:
                        datapackage = response.read().decode('utf-8')
                        datapackage_json = json.loads(datapackage)

                        # find schema corresponding to uploaded file
                        uploaded_file_schema = None

                        for resource in datapackage_json.get('resources', []):

                            print('resource', resource)

                            print('path' in list(resource.keys()))

                            if 'path' in list(resource.keys()) and file_name in resource['path']:
                                print('found')
                                uploaded_file_schema = resource['schema']
                                break


                        if uploaded_file_schema:

                            # convert dictionary schema into frictionless schema object
                            schema = Schema(uploaded_file_schema)

                            # perform validation using schema matched to uploaded file
                            report = validate(file, schema=schema)
                            
                            return schema + '\n' + report

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
    },
    "Français": {
        "title": "Contrôle de qualité CSV avec Frictionless",
        "upload": "Télécharger un fichier CSV",
        "uploaded_success": "Fichier téléchargé avec succès !",
        "check_button": "Vérifier",
        "error": "Erreur de validation:",
        "validation_complete": "Validation terminée !",
    },
    "Italiano": {
        "title": "Controllo qualità CSV con Frictionless",
        "upload": "Caricare un file CSV",
        "uploaded_success": "File caricato con successo!",
        "check_button": "Controllo",
        "error": "Errore durante la validazione:",
        "validation_complete": "Validazione completata!",
    },
    "English": {
        "title": "CSV Quality Check with Frictionless",
        "upload": "Upload a CSV file",
        "uploaded_success": "File uploaded successfully!",
        "check_button": "Check",
        "error": "Error during validation:",
        "validation_complete": "Validation complete!",
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
        if st.button(translation["check_button"]):
            progress_bar = st.progress(0)
            report = perform_quality_check(uploaded_file)

            if isinstance(report, str):
                st.error(f"{translation['error']} {report}")
            else:
                st.success(translation["validation_complete"])
                st.write(report)

if __name__ == "__main__":
    main()

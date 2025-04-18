# Package per salvare e rileggere il file su github
from github import Github
import pickle
import streamlit as st
import pyAesCrypt

def upload_file(username,token, df,repository_name, file_path ):#username, token, file_path):
    
    encoded_data = pickle.dumps(df)
    g = Github(username,token)

    try:
        repo = g.get_user().get_repo(repository_name)
    except Exception as e:
        st.write("Error accessing repository:", e)
        exit()
    
    try:    
        file = repo.get_contents(file_path)
        repo.update_file(file_path, "Updated data", encoded_data, file.sha)
        st.success("File updated successfully.")
    except:
        repo.create_file(file_path, 'File created', encoded_data)

def retrieve_file(username, token,repository_name, file_path):#username,token, file_path):
    g = Github(username,token)

    # Get repository
    try:
        repo = g.get_user().get_repo(repository_name)
    except Exception as e:
        st.write("Error accessing repository:", e)
        exit()
    contents = repo.get_contents(file_path)
    content_string = contents.decoded_content
    loaded_data = pickle.loads(content_string)
    
    return loaded_data

def upload_file_encrypt(username,token, df,repository_name, file_path, psw ):#username, token, file_path):
    
    #encoded_data_in = pickle.dumps(df)
    def create_pickle(picklefile):
        data = df
        with open(picklefile, "wb") as outfile:
            pickle.dump(data, outfile)
    
    picklefile = "somefile.pkl"
    encoded_data_out = f"{picklefile}.aes"
    create_pickle(picklefile)
    pyAesCrypt.encryptFile(picklefile, encoded_data_out, psw)

    st.write(encoded_data_out)
    g = Github(username,token)

    try:
        repo = g.get_user().get_repo(repository_name)
    except Exception as e:
        st.write("Error accessing repository:", e)
        exit()
    
    try:    
        file = repo.get_contents(file_path)
        repo.update_file(file_path, "Updated data", encoded_data_out, file.sha)
        st.success("File updated successfully.")
    except:
        repo.create_file(file_path, 'File created', encoded_data_out)

def retrieve_file_decrypt(username, token,repository_name, file_path,psw):#username,token, file_path):

    picklefile = "somefile.pkl"
    encoded_data_out = f"{picklefile}.aes"

    g = Github(username,token)
    # Get repository
    try:
        repo = g.get_user().get_repo(repository_name)
    except Exception as e:
        st.warning(f'"Error accessing repository:" {e}')
        exit()

    pyAesCrypt.decryptFile(encoded_data_out, f"2_{picklefile}", psw)

    with open(f"2_{picklefile}", "rb") as infile:
        loaded_data = pickle.load(infile)

    return loaded_data
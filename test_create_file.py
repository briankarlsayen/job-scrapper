import os
import pandas as pd
from utils import save_to_textfile
from datetime import date

today = date.today()
formatted_date = today.strftime("%Y_%m_%d")

def create_job_folder(folder_name: str, file_name: str, text_content: str, csv_content: list):
    text_file_name = f"{file_name}.txt"
    csv_file_name = f"{file_name}.csv"
    folder_path =  os.path.join("datas", folder_name)
    os.makedirs(folder_path, exist_ok=True)
    text_file_path = os.path.join(folder_path, text_file_name)
    csv_file_path = os.path.join(folder_path, csv_file_name)

    # create text file
    save_to_textfile(text_file_path, "\n".join(text_content))

    # create csv file
    df = pd.DataFrame(csv_content)
    df.to_csv(csv_file_path, sep=';', index=False)

    
create_job_folder(folder_name=formatted_date, file_name="jobstreet", text_content="this is the voice", csv_content=[{'title': 'the job', 'job_description': 'software development'}])

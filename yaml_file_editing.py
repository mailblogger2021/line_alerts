import datetime
import yaml
import os
def yaml_file_edit(minutes,file_name):
    current_time = datetime.datetime.now()
    cron_time = current_time + datetime.timedelta(minutes=minutes)

    cron_value = f"{cron_time.minute} {cron_time.hour} {cron_time.day} {cron_time.month} *"

    current_directory = os.getcwd()
    all_directories = []
    for root, dirs, files in os.walk(current_directory):
        all_directories.extend([os.path.join(root, d) for d in dirs])
    print("All directories in the current directory and its subdirectories:")
    for directory in all_directories:
        print(directory)
    yaml_file_path = f'.github/workflows/{file_name}.yml'
    with open(yaml_file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)

    yaml_data['on']['schedule'][0]['cron'] = cron_value 

    with open(yaml_file_path, 'w') as file:
        yaml.dump(yaml_data, file)

if __name__=="__main__":
    yaml_file_edit(50,"main")
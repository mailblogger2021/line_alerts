import datetime
import yaml
import os
def yaml_file_edit(minutes,file_name):
    current_time = datetime.datetime.now()
    cron_time = current_time + datetime.timedelta(minutes=minutes)

    cron_value = f"{cron_time.minute} {cron_time.hour} {cron_time.day} {cron_time.month} *"

    file_name = "day"
    yaml_file_path = f'.github/workflows/{file_name}.yml'
    with open(yaml_file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)

    yaml_data['on']['schedule'][0]['cron'] = cron_value 

    with open(yaml_file_path, 'w') as file:
        yaml.dump(yaml_data, file)

if __name__=="__main__":
    yaml_file_edit(50,"main")
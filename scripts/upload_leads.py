import json
import os
import re
import pandas as pd
import numpy as np
import datetime
import requests
from dateutil.parser import parse

BASE_URL = '64.227.150.234' #'127.0.0.1'
use_cols = ['name', 'lead_date', 'phone_num', 'email', 'course_id', 'batch_time', 'source_id', 'area',
            'details_sent', 'remark', 'agent_id', 'demo_date', 'visit_date', 'broadcast']


def read_from_csv(path):
    df = pd.read_csv(path)
    df = df.where(pd.notnull(df), None)
    df.head(5)
    return df


def read_from_excel(path, sheet_name):
    df = pd.read_excel(path, sheet_name=sheet_name)
    df = df.where(pd.notnull(df), None)
    return df


def specific_date_parsing(df):
    df.loc[df['lead_date'] == '30 - Marc', 'lead_date'] = '2021-03-30'
    df.loc[df['lead_date'] == '16 aprli', 'lead_date'] = '2021-04-16'
    df.loc[df['lead_date'] == '17 aprli', 'lead_date'] = '2021-04-17'
    df.loc[df['lead_date'] == '20-Oct :', 'lead_date'] = '2021-10-20'
    df.loc[df['lead_date'] == '6-DE', 'lead_date'] = '2021-12-06'
    df.loc[df['lead_date'] == '2021-nan-nan', 'lead_date'] = '2021-01-01'
    df.loc[df['lead_date'] == '2022-nan-nan', 'lead_date'] = '2022-01-01'
    df.loc[df['lead_date'] == 'PD', 'lead_date'] = '2022-03-01'
    df.loc[df['lead_date'] == 'SSS', 'lead_date'] = '2022-03-01'
    df.loc[df['lead_date'] == 'DOne', 'lead_date'] = '2022-05-01'
    df.loc[df['lead_date'] == 'Done', 'lead_date'] = '2022-05-01'
    df.loc[df['lead_date'] == 'DONE', 'lead_date'] = '2022-05-01'
    df.loc[df['lead_date'] == 'done', 'lead_date'] = '2022-05-01'
    df.loc[df['lead_date'] == 'na', 'lead_date'] = '2022-05-01'
    df.loc[df['lead_date'] == '23/07/2021\n4-Oct', 'lead_date'] = '2022-10-04'
    return df


def any_date_parser(date_, year):
    if type(date_) is str:
        date_ = parse(date_)
    elif (date_ is None) or (type(date_) is int):
        return f'{datetime.datetime.now().year}-01-01'
    month_ = f'0{date_.month}' if date_.month < 10 else f'{date_.month}'
    day_ = f'0{date_.day}' if date_.day < 10 else f'{date_.day}'

    if year:
        return f"{year}-{month_}-{day_}"
    else:
        return f"{date_.year}-{month_}-{day_}"


def parse_date(date_):
    # only allow date format '2000-10-01'
    try:
        if type(date_) is str:
            return datetime.datetime.strptime(date_, '%Y-%m-%d')
        elif (date_ is None) or (type(date_) is int):
            return f'{datetime.datetime.now().year}-01-01'
        else:
            return date_.strftime('%Y-%m-%d')
    except ValueError:
        raise ValueError('Invalid lead_date. Check excel data.')
    except TypeError as ex:
        raise TypeError(f'Invalid lead_date date format. {str(ex)}')


def replace_new_line_in_col(df):
    df.columns = [re.sub(r'\s\s\s+', '', str(c)) for c in df.columns]
    df.columns = [c.replace("\n", "_") for c in df.columns]
    return df


def rename_column_in_df(df):
    rename_cols = {
        'Date': 'lead_date',
        'Name': 'name',
        'Name ': 'name',
        'NAME': 'name',
        'Number': 'phone_num',
        'Number ': 'phone_num',
        'Number March': 'phone_num',
        'Number April': 'phone_num',
        'Number May': 'phone_num',
        'Number June': 'phone_num',
        'Number July': 'phone_num',
        'Number Sept': 'phone_num',
        'Email': 'email',
        'Online/_Offline': 'course_id',
        'Online/Offline': 'course_id',
        'Lead Source': 'source_id',
        'Lead _Source': 'source_id',
        'Details _Send': 'details_sent',
        'Details_Sent': 'details_sent',
        'Details _Sent': 'details_sent',
        'Details _sent': 'details_sent',
        'Details sent': 'details_sent',
        'Details Sent': 'details_sent',
        'Area': 'area',
        'Details Send': 'details_sent',
        'Remark': 'remark',
        'Remarks': 'remark',
        'Batch_ Timing': 'batch_time',
        'Visit Date_( Pitch by)': 'visit_date',
        'Remark   ': 'remark',
        'SSS Lead transfered to': 'agent_id',
        ' Lead Off': 'agent_id',
        'LEADS OFF': 'agent_id',
        'Lead To': 'agent_id',
        'Lead to': 'agent_id',
        'Leads': 'agent_id',
        'Leads off': 'agent_id',
        'Leads to': 'agent_id',
        ' Date_': 'lead_date',
        ' Date__': 'lead_date',
        'Broadcast': 'broadcast',
        'Broadcaste': 'broadcast',
        'Demo Date (Trainer Name)': 'demo_date'
    }
    df = df.rename(columns=rename_cols)
    return df


def verify_columns(df):
    for required_col in use_cols:
        if required_col not in df.columns:
            raise ValueError(f'Column {required_col} not found.')
    return df


def drop_unneccessary_columns(df):
    for col in df.columns:
        if col not in use_cols:
            df.drop(col, axis=1, inplace=True)
    return df


def set_batch_time(df):
    df['batch_time'].fillna('Morning', inplace=True)
    df.loc[df['batch_time'].str.lower().str.strip() == 'afternoon', 'batch_time'] = 'Afternoon'
    df.loc[df['batch_time'].str.lower().str.strip() == 'morning', 'batch_time'] = 'Morning'
    df.loc[df['batch_time'].str.lower().str.strip() == 'evening', 'batch_time'] = 'Evening'
    df.loc[df['batch_time'].str.lower().str.strip() == 'morning ', 'batch_time'] = 'Morning'
    df['batch_time'].fillna('Morning', inplace=True)

    df.loc[df['batch_time'] == 'Morning', 'batch_time'] = 1
    df.loc[df['batch_time'] == 'Afternoon', 'batch_time'] = 2
    df.loc[df['batch_time'] == 'Evening', 'batch_time'] = 3
    df.loc[~df['batch_time'].isin([1, 2, 3]), 'batch_time'] = 1  # others
    return df


def set_course(df):
    df['course_id'].fillna('offline', inplace=True)
    df.loc[df['course_id'].str.lower().str.strip() == 'hinjewadi', 'course_id'] = 'offline'
    df.loc[df['course_id'].str.lower().str.strip() == 'online', 'course_id'] = 'online'
    df.loc[df['course_id'].str.lower().str.strip() == 'oflfline', 'course_id'] = 'offline'
    df.loc[df['course_id'].str.lower().str.strip() == 'on\;ine', 'course_id'] = 'online'
    df.loc[df['course_id'].str.lower().str.strip() == 'onine', 'course_id'] = 'online'
    df.loc[df['course_id'].str.lower().str.strip() == 'oflline', 'course_id'] = 'offline'
    df.loc[df['course_id'].str.lower().str.strip() == 'On line', 'course_id'] = 'online'
    df.loc[df['course_id'].str.lower().str.strip() == 'Offlline', 'course_id'] = 'offline'
    df.loc[df['course_id'].str.lower().str.strip() == 'offfline', 'course_id'] = 'offline'
    df.loc[df['course_id'].str.lower().str.strip() == 'offline batch', 'course_id'] = 'offline'
    df.loc[df['course_id'].str.lower().str.strip() == 'Offlne', 'course_id'] = 'offline'
    df.loc[df['course_id'].str.lower().str.strip() == 'online ', 'course_id'] = 'online'
    df.loc[df['course_id'].str.lower().str.strip() == 'offline/ online', 'course_id'] = 'online'
    df.loc[df['course_id'].str.lower().str.strip() == 'offline', 'course_id'] = 'offline'
    df.loc[df['course_id'].str.lower().str.strip() == 'offline/online', 'course_id'] = 'online'
    df.loc[df['course_id'].str.lower().str.strip() == 'online/ offline', 'course_id'] = 'online'
    df.loc[df['course_id'].str.lower().str.strip() == 'online/ offlineon', 'course_id'] = 'online'
    df.loc[df['course_id'].str.lower().str.strip() == 'online/ offlineonl', 'course_id'] = 'online'
    df.loc[df['course_id'].str.lower().str.strip() == 'offlne', 'course_id'] = 'offline'
    df.loc[df['course_id'].str.lower().str.strip() == 'offline', 'course_id'] = 'offline'
    df.loc[df['course_id'].str.lower().str.strip() == 'offline ', 'course_id'] = 'offline'
    df.loc[df['course_id'].str.lower().str.strip() == 'walk-in', 'course_id'] = 'offline'
    df.loc[df['course_id'].str.lower().str.strip() == 'online (weekend)', 'course_id'] = 'offline'
    df.loc[df['course_id'].str.lower().str.strip() == 'on/off', 'course_id'] = 'offline'
    df.loc[df['course_id'].str.lower().str.strip() == 'on/ off', 'course_id'] = 'offline'
    df.loc[df['course_id'].str.lower().str.strip() == 'offlinhr', 'course_id'] = 'offline'
    df.loc[df['course_id'].str.lower().str.strip() == 'oonline', 'course_id'] = 'online'
    df.loc[df['course_id'].str.lower().str.strip() == 'on+ off', 'course_id'] = 'offline'
    df.loc[df['course_id'].str.lower().str.strip() == 'nan', 'course_id'] = 'offline'
    df.loc[df['course_id'] == np.nan, 'course_id'] = 'offline'
    df['course_id'].fillna('offline', inplace=True)

    df.loc[df['course_id'] == 'offline', 'course_id'] = 1
    df.loc[df['course_id'] == 'online', 'course_id'] = 2
    df.loc[~df['course_id'].isin([1, 2]), 'course_id'] = 1  # others
    return df


def set_source(df):
    df['source_id'].fillna('Direct Call', inplace=True)
    df.loc[df['source_id'].str.lower().str.strip() == 'offline', 'source_id'] = 'Direct Call'
    df.loc[df['source_id'].str.lower().str.strip() == 'offline', 'source_id'] = 'Direct Call'
    df.loc[df['source_id'].str.lower().str.strip() == 'call', 'source_id'] = 'Direct Call'
    df.loc[df['source_id'].str.lower().str.strip() == 'vadagaon sheri', 'source_id'] = 'Direct Call'
    df.loc[df['source_id'].str.lower().str.strip() == 'walk-in', 'source_id'] = 'Walk-in'
    df.loc[df['source_id'].str.lower().str.strip() == 'vijay', 'source_id'] = 'Direct Call'
    df.loc[df['source_id'].str.lower().str.strip() == 'kondawa ', 'source_id'] = 'Direct Call'
    df.loc[df['source_id'].str.lower().str.strip() == 'walk-in', 'source_id'] = 'Walk-in'
    df.loc[df['source_id'].str.lower().str.strip() == 'call', 'source_id'] = 'Direct Call'
    df.loc[df['source_id'].str.lower().str.strip() == 'called vIjay', 'source_id'] = 'Direct Call'
    df.loc[df['source_id'].str.lower().str.strip() == 'walk- in', 'source_id'] = 'Walk-in'
    df.loc[df['source_id'].str.lower().str.strip() == ']walk-in', 'source_id'] = 'Walk-in'
    df.loc[df['source_id'].str.lower().str.strip() == 'walk - in', 'source_id'] = 'Walk-in'
    df.loc[df['source_id'].str.lower().str.strip() == 'walkin', 'source_id'] = 'Walk-in'
    df.loc[df['source_id'].str.lower().str.strip() == 'vijay', 'source_id'] = 'Direct Call'
    df.loc[df['source_id'].str.lower().str.strip() == 'chandan nagar', 'source_id'] = 'Direct Call'
    df.loc[df['source_id'].str.lower().str.strip() == 'whats app', 'source_id'] = 'Whatsapp'
    df.loc[df['source_id'].str.lower().str.strip() == 'reference', 'source_id'] = 'Referal'
    df.loc[df['source_id'].str.lower().str.strip() == 'ref simran', 'source_id'] = 'Referal'
    df.loc[df['source_id'].str.lower().str.strip() == 'ref vijay', 'source_id'] = 'Referal'
    df.loc[df['source_id'].str.lower().str.strip() == 'ref sumit', 'source_id'] = 'Referal'
    df.loc[df['source_id'].str.lower().str.strip() == 'ref chaitanya d', 'source_id'] = 'Referal'
    df['source_id'].fillna('Direct Call', inplace=True)

    df.loc[df['source_id'] == 'Whatsapp', 'source_id'] = 3
    df.loc[df['source_id'] == 'Direct Call', 'source_id'] = 4
    df.loc[df['source_id'] == 'Walk-in', 'source_id'] = 5
    df.loc[df['source_id'] == 'Referal', 'source_id'] = 7
    df.loc[~df['source_id'].isin([3, 4, 5, 7]), 'source_id'] = 4  # others

    return df


def set_details_sent(df):
    df['details_sent'].fillna('no', inplace=True)
    df.loc[df['details_sent'].str.lower().str.strip().isin(['y', 'yes', 'offline', 'ya']), 'details_sent'] = 1
    df.loc[~df['details_sent'].isin([1]), 'details_sent'] = 2  # others
    return df


def set_broadcast(df):
    df['broadcast'].fillna('no', inplace=True)
    df.loc[df['broadcast'].str.lower().str.strip().isin(['y', 'yes', 'offline', 'ya']), 'broadcast'] = 1
    df.loc[~df['broadcast'].isin([1]), 'broadcast'] = 2  # others
    return df


def is_record_exist(phone_num):
    url = f"https://{BASE_URL}:3002/api/leads/by_email_or_phone_num?phone_num={phone_num}"
    headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.AHMxv1ZyUSH21Iq3Cb6AFbXgFQjrsOADGcSm83UG770'
    }
    response = requests.request("GET", url, headers=headers, verify=False)
    #     print(response.text)
    if response.json():
        return True
    return False


def save_lead(df):
    leads_not_saved = []
    for index, row in df.iterrows():
        # Create lead
        url = f"https://{BASE_URL}:3002/api/leads/add"

        if 'NaT' in row['lead_date']:
            continue

        if not row['phone_num']:
            continue
        phone_alt_num = str(row['phone_num'])
        if '/' in phone_alt_num:
            phone_alt_num = phone_alt_num.split('/')
        else:
            phone_alt_num = phone_alt_num.split('\n')
        if not phone_alt_num:
            continue

        if len(phone_alt_num) == 2:
            phone_num = '+91-' + phone_alt_num[0].replace(' ', '')
            phone_num = phone_num.strip()
            alternate_phone_num = '+91-' + phone_alt_num[1].replace(' ', '')
            alternate_phone_num = alternate_phone_num.strip()
        else:
            phone_num = '+91-' + phone_alt_num[0].replace(' ', '')
            phone_num = phone_num.strip()
            alternate_phone_num = None

        if is_record_exist(phone_num.replace('+', '%2B')):
            continue

        payload = json.dumps([
            {
                "name": row['name'],
                "phone_num": phone_num,
                "alternate_phone_num": alternate_phone_num,
                "email": row['email'].strip() if row['email'] else None,
                "lead_date": row['lead_date'].strip(),
                "remarks": row['remark'],
                "country_id": 98,
                "area": row['area'],
                "city_id": 1,
                "branch_id": 1,
                "source_id": row['source_id'],
                "course_id": row['course_id'],
                "batch_time_id": 1,
                "next_action_date": None,
                "next_action_remarks": None,
                "details_sent": row['details_sent'],
                "visit_date": None,
                "pitch_by": None,
                "demo_date": None,
                "instructor": None,
                "broadcast": row['broadcast'],
                "agent_id": 1,
                "fee_offer": None,
                "is_student": 0
            }
        ])
        headers = {
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.AHMxv1ZyUSH21Iq3Cb6AFbXgFQjrsOADGcSm83UG770',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        if 'error' in response.json():
            # print()
            # print(response.json())
            leads_not_saved.append({'name': row['name'], 'phone_num': phone_num, 'email': row['email']})
            # print(payload)
    return leads_not_saved


def save_txt(file_name, txt_file_path, leads_not_saved):
    output_txt = f"""
        
    """
    leads_not_saved = [list(x.values()) for x in leads_not_saved]
    print('leads_not_saved: ', leads_not_saved)
    with open(txt_file_path, 'w') as fp:

        fp.write('Following are the missing leads: ' + '\n\n')
        fp.write('Use below Name & Phone Number and search in your original document. \n'
                 'Please check and add them manually. -> ' + file_name + '\n\n\n')
        for index, x in enumerate(leads_not_saved):
            info = ', '.join(filter(None, x))
            fp.write(f'{str(index + 1)} => {info}')
            fp.write('\n\n')


def run_manual(path):
    file_name = os.path.basename(path).split('.')[0]
    df = read_from_excel(path, sheet_name=0)
    print('df: ', df)
    df = replace_new_line_in_col(df)
    df = rename_column_in_df(df)
    df = verify_columns(df)
    df = drop_unneccessary_columns(df)
    df = specific_date_parsing(df)
    df['lead_date'] = df['lead_date'].apply(any_date_parser, year=2022)
    df = specific_date_parsing(df)
    df = set_batch_time(df)
    df = set_course(df)
    df = set_source(df)
    df = set_details_sent(df)
    df = set_broadcast(df)
    leads_not_saved = save_lead(df)
    txt_file_path = f'{file_name}.txt'
    save_txt(file_name, txt_file_path, leads_not_saved)


def run(binary_path):
    df = read_from_excel(binary_path, sheet_name=0)
    df = replace_new_line_in_col(df)
    df = rename_column_in_df(df)
    df = verify_columns(df)
    df = drop_unneccessary_columns(df)
    df = specific_date_parsing(df)
    df['lead_date'] = df['lead_date'].apply(parse_date)
    df = specific_date_parsing(df)
    df = set_batch_time(df)
    df = set_course(df)
    df = set_source(df)
    df = set_details_sent(df)
    df = set_broadcast(df)
    leads_not_saved = save_lead(df)
    return leads_not_saved


if __name__ == '__main__':
    # for x_file_name in os.listdir('.'):
    #     print('file name: ', x_file_name)
        # if '.xlsx' in x_file_name and x_file_name != 'Summer Internship.xlsx' and x_file_name != 'pcmc.xlsx' \
        #         and x_file_name != 'new.xlsx':
        #     run_manual(x_file_name)
    x_file_name = 'Dec22.xlsx'
    run_manual(x_file_name)

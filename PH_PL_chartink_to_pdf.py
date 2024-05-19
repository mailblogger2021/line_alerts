import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from fpdf import FPDF
import sys
import two_line_pattern_detect as two_line
import threading
import logging
import os
import json

def chartink_to_pdf(session,title, pdf,chartink_url):
    r = session.post('https://chartink.com/screener/process', data={'scan_clause': chartink_url}).json()
    df = pd.DataFrame(r['data'])
    if df.empty:
        return []
    
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 20, title, ln=True)
    pdf.ln(2)
    
    table_cell_height = 6
    
    cols = df.columns
    content = df.values.tolist()
    
    max_widths = [pdf.get_string_width(col) for col in cols]
    for row in content:
        for i, cell in enumerate(row):
            width = pdf.get_string_width(str(cell))*50//100
            if width > max_widths[i]:
                max_widths[i] = width
    
    pdf.set_font('Arial', '', 6)
    cols = df.columns
    for i, col in enumerate(cols):
        pdf.cell(max_widths[i], table_cell_height, col, align='C', border=1)
    pdf.ln(table_cell_height)

    for row in content:
        for i, cell in enumerate(row):
            # Set cell width based on maximum content width in the column
            pdf.cell(max_widths[i], table_cell_height, str(cell), align='C', border=1)
        pdf.ln(table_cell_height)
    pdf.ln(10)
    # if not df.empty:
    return df['nsecode'].unique().tolist()
    # else:
        # return []

def generate_chartink_code(time_frame_list=[],base_code_list=[],title_list=[],file_name='chartink_data_pdf'):
    
    pdf = FPDF(unit='mm', format=(250, 297))
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)

    ph_pl_list = {}
    with requests.Session() as session:
        r = session.get('https://chartink.com/screener/time-pass-48')
        soup = bs(r.content, 'lxml')
        session.headers['X-CSRF-TOKEN'] = soup.select_one('[name=csrf-token]')['content']
        for time_frame,base_code, title in zip(time_frame_list,base_code_list, title_list):
            ph_pl_list[time_frame] = chartink_to_pdf(session,title,pdf,base_code)

    pdf.output(f'{file_name}.pdf', 'F')
    return ph_pl_list

if __name__ =="__main__":
    
    time_frames = ["day","week","month","quarter"]
    if(len(sys.argv) >= 2):
        time_frames = (sys.argv[1]).split(',')

    logging.basicConfig(filename=f'logfile_ph_pl_{",".join(time_frames)}.log',level=logging.INFO, format='%(asctime)s -%(levelname)s - %(message)s')
    logging.info(f"Started...")
    time_frames_dict = {
                "day" : ["days","daily"],
                "week" : ["weeks","weekly"],
                "month" : ["months","monthly"],
                "quarter" : ["quarter","quarterly"]
            }
    time_frames_for_yfinance = {
                "day" : "1d",
                "week" : "1wk",
                "month" : "1mo",
                "quarter" : "3mo"
            }
    day_ph_pl = "( {33489} ( ( {33489} ( 10 days ago high > latest max ( 10 , 11 days ago high ) and 10 days ago high >= latest max ( 10 , latest high ) ) ) or ( {33489} ( 10 days ago low < latest min ( 10 , 11 days ago low ) and 10 days ago low <= latest min ( 10 , latest low ) ) ) ) )"

    base_code_list,title_list,time_frame_list = [],[],[]
    # time_frames = time_frames[:1]
    for time_frame in time_frames:
        time_frame_dict = time_frames_dict[time_frame]
        base_code = day_ph_pl.replace("days",time_frame_dict[0]).replace("latest",time_frame_dict[1])
        time_frame_list.append(time_frame)
        base_code_list.append(base_code)
        title_list.append(time_frame_dict[1]+" time Frame new PH PL ")
        # two_line.generate_url_yfinance()
    pdf_file_name = "PH_PL_chartink_to_pdf"
    ph_pl_list = generate_chartink_code(time_frame_list,base_code_list,title_list,pdf_file_name)
    threads = []
    for time_frame in ph_pl_list:
        stock_lists = ph_pl_list[time_frame]
        stock_lists = [stock+".NS" for stock in stock_lists]
        # stock_lists = stock_lists[:1]
        yfinance_time_frame = time_frames_for_yfinance[time_frame]
        try:
            two_line.three_line_file_name = f"three_line_alerts_{yfinance_time_frame}.xlsx"
            two_line.two_line_file_name = f"two_line_alerts_{yfinance_time_frame}.xlsx"
            two_line.data_store_file_name = f"data_store_{yfinance_time_frame}.json"

            isExist = os.path.exists(two_line.two_line_file_name)
            if(isExist):
                two_line.three_line_alert_df = pd.read_excel(two_line.three_line_file_name)

            isExist = os.path.exists(two_line.two_line_file_name)
            if(isExist):
                two_line.two_line_alert_df = pd.read_excel(two_line.two_line_file_name)

            isExist = os.path.exists(two_line.data_store_file_name)
            if isExist:
                with open(two_line.data_store_file_name, "r") as file:
                    two_line.data_store = json.load(file)
            else:
                two_line.data_store = {}
            two_line.generate_url_yfinance(stock_lists,yfinance_time_frame)
            # thread = threading.Thread(target=two_line.generate_url_yfinance, 
            #                         args=(stock_lists,time_frames_for_yfinance[time_frame]))
            # threads.append(thread)
            # thread.start()

        except Exception as e:
            print(f"{time_frame} - Error in isPivot function: {e}")
    # for thread in threads:
    #     thread.join()
    print(ph_pl_list)
import re
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

# """
# 101(含)以前是IFRS之前;
# 102 以後是IFRS之後
# """

def IFRS_After(*args):
    YEAR = args[0]
    STOCK = args[1]
    SEASON = args[2]
    # 綜合資產負債表(IFRS後)
    BalanceSheetURL_After101 = "ttps://mops.twse.com.tw/mops/web/ajax_t163sb05?encodeURIComponent=1&step=1&firstin=1&off=1&isQuery=Y&TYPEK=sii&year={}&season=0{}".format(YEAR, SEASON)

    # 綜合損益表(IFRS後)
    ProfitAndLoseURL_After101 = "https://mops.twse.com.tw/mops/web/ajax_t163sb04?encodeURIComponent=1&step=1&firstin=1&off=1&isQuery=Y&TYPEK=sii&year={}&season=0{}".format(YEAR, SEASON)

    # 現金流量表(IFRS後): 僅試用一般股
    CashFlowStatementURL_After101 = "https://mops.twse.com.tw/mops/web/ajax_t164sb05?encodeURIComponent=1&step=1&firstin=1&off=1&keyword4=&code1=&TYPEK2=&checkbtn=&queryName=co_id&inpuType=co_id&TYPEK=all&isnew=false&co_id={}&year={}&season=0{}".format(STOCK, YEAR, SEASON)
    
    # FinancialAccountingList_After = [BalanceSheetURL_After101, ProfitAndLoseURL_After101, CashFlowStatementURL_After101]
    FinancialAccountingList_After = [BalanceSheetURL_After101]
    return FinancialAccountingList_After


def IFRS_Before(*args):
    YEAR = args[0]
    STOCK = args[1]
    SEASON = args[2]
    # 合併資產負債表(IFRS前)
    BalanceSheetURL_with_all_Before101 = 'https://mops.twse.com.tw/mops/web/ajax_t51sb12?encodeURIComponent=1&step=1&firstin=1&off=1&isQuery=Y&TYPEK=sii&year={}&season=0{}'.format(YEAR, SEASON)

    # 合併損益表(IFRS前)
    ProfitAndLoseURL_with_all_Before101 = 'https://mops.twse.com.tw/mops/web/ajax_t51sb13?encodeURIComponent=1&step=1&firstin=1&off=1&isQuery=Y&TYPEK=sii&year={}&season=0{}'.format(YEAR, SEASON)

    # 現金流量表(IFRS前): 僅試用一般股(表格特殊)
    CashFlowStatementURL_with_all_Before101 = 'https://mops.twse.com.tw/mops/web/ajax_t05st39?encodeURIComponent=1&step=1&firstin=1&off=1&keyword4=&code1=&TYPEK2=&checkbtn=&queryName=co_id&inpuType=co_id&TYPEK=all&isnew=false&co_id={}&year={}&season=0{}'.format(STOCK, YEAR, SEASON)

    # FinancialAccountingList_Before = [BalanceSheetURL_with_all_Before101, ProfitAndLoseURL_with_all_Before101, CashFlowStatementURL_with_all_Before101]
    FinancialAccountingList_Before = [BalanceSheetURL_with_all_Before101]
    return FinancialAccountingList_Before


def IFRS_Divide(*args):
    YEAR = args[0]
    STOCK = args[1]
    # 股息股利
    DividendURL = 'https://mops.twse.com.tw/mops/web/ajax_t05st09?encodeURIComponent=1&step=1&firstin=1&off=1&keyword4=&code1=&TYPEK2=&checkbtn=&queryName=co_id&inpuType=co_id&TYPEK=all&isnew=false&co_id={}&year={}'.format(STOCK, YEAR)

    # 財務報表 + 股息股利 列表：
    Dividend = [DividendURL]
    return Dividend



def crawl_financial_Report(*args):
    url = args[0]
    ifrs = args[1]
    financial_stock_list = [2801, 2809, 2812, 2836, 2838, 2845, 2849, 2832, 2880, 2881,
                            2882, 2883, 2884, 2885, 2886, 2887, 2888, 2889, 2890, 2891, 2892, 
                            2855, 6005, 6012, 6024, 1409, 1718, 2514, 2905]
    r = requests.get(url)
    r.encoding = 'utf8'
    if ifrs == 'AFTER':
        if ('ajax_t164sb05' in url) :
            check_stock = re.split(r'co_id=',url)[1].split('&')[0]
            if not int(check_stock) in financial_stock_list:  # 只走 現金流量表(IFRS前) & 一般股 (表格特殊)
                dfs = pd.read_html(r.text)[1].fillna("")
                return dfs
        else: 
            # dfs = pd.read_html(r.text)[1].fillna("")
            dfs = pd.read_html(r.text, header=None)
            return dfs # 走負債跟損益表

    elif ifrs == 'BEFORE':
        dfs = pd.read_html(r.text, header=None)
        # dfs = pd.read_html(r.text)[1].fillna("")
        if ('ajax_t05st39' in url) :
            check_stock = re.split(r'co_id=',url)[1].split('&')[0]
            if not int(check_stock) in financial_stock_list: # 只走 現金流量表(IFRS前) & 一般股 (表格特殊)
                return r.text
        else: 
            return dfs # 走負債跟損益表


# def call_FinancialAccountingList(year, stocks):
#     if year > 101: 
#         for season in range(1,4+1):
#             FinancialAccountingList_After = IFRS_After(year, stocks, season)
#             for fa in FinancialAccountingList_After:
#                 report = crawl_financial_Report(fa, 'AFTER')
#                 print(report)
#     else:
#         for season in range(1,4+1):
#             FinancialAccountingList_Before = IFRS_Before(year, stocks, season)
#             for fa in FinancialAccountingList_Before:
#                 report = crawl_financial_Report(fa, 'BEFORE')
#                 print(report)
#     return 

# def call_by_year(stocks):
#     YEAR_List_Before101 = range(97,101+1)
#     for year in YEAR_List_Before101:
#         _ = call_FinancialAccountingList(year, stocks)

#     YEAR_List_After101 = range(102,109+1)
#     for year in YEAR_List_After101:
#         _ = call_FinancialAccountingList(year, stocks)
#     return 



############################################  [TEST]   ########################################################
def call_FinancialAccountingList(year, stocks):
    if year > 101: 
        for season in [1]:
            FinancialAccountingList_After = IFRS_After(year, stocks, season)
            for fa in FinancialAccountingList_After:
                print('*****************************     [ AFTER: {}  ]       **************************************'.format(fa))
                report = crawl_financial_Report(fa, 'AFTER')
                
                # 現金流量：
                if 'ajax_t164sb05' in fa and report:
                    report = (report.iloc[:,0:2])
                    report.columns = ['會計項目','金額']
                    df1 = (report[report['會計項目'] == '營業活動之淨現金流入（流出）']).values.tolist()[0]
                    df1 = pd.DataFrame([df1[1]], columns=[df1[0]])
                    df2 = (report[report['會計項目'] == '投資活動之淨現金流入（流出）']).values.tolist()[0]
                    df2 = pd.DataFrame([df2[1]], columns=[df2[0]])
                    df3 = (report[report['會計項目'] == '籌資活動之淨現金流入（流出）']).values.tolist()[0]
                    df3 = pd.DataFrame([df3[1]], columns=[df3[0]])
                    df1df2 = pd.concat([df1, df2], axis=1)
                    pd_combine = pd.concat([df1df2, df3], axis=1)
                    pd_combine.columns = ['營業活動之淨現金流入（流出）','投資活動之淨現金流入（流出）', '融資or籌資活動之淨現金流入（流出）']
                    print(pd_combine.to_markdown())
                
                # 合併損益:
                elif 'ajax_t163sb04' in fa:
                    report = report[1:]
                    report = [i.set_index('公司代號') for i in report]
                    for i in report:
                        if int(stocks) in i.index:
                            got = i.loc[int(stocks)]
                            got = got.to_frame().T
                            print(got.to_markdown())
                            break

                     
    else:
        for season in [1]:
            FinancialAccountingList_Before = IFRS_Before(year, stocks, season)
            for fa in FinancialAccountingList_Before:
                print('*****************************     [ BEFORE: {}  ]       **************************************'.format(fa))
                report = crawl_financial_Report(fa, 'BEFORE')
                
                # 現金流量：
                if 'ajax_t05st39' in fa and report:
                    report_all = re.findall(r'.*淨現金流.*', report)
                    pd_combine = pd.DataFrame()
                    for ra in report_all:   
                        report_list_temp = [ i for i in ((ra.lstrip()).rstrip()).split(' ') if i!='']
                        report_list_temp = [i.strip('(') for i in report_list_temp]
                        report_list_temp = [i.strip(')') for i in report_list_temp]
                        report_list_temp = [i for i in report_list_temp if i!='']
                        pd_temp = pd.DataFrame([report_list_temp[1]], columns=[report_list_temp[0]])
                        pd_combine = pd.concat([pd_combine, pd_temp], axis=1)
                    pd_combine.columns = ['營業活動之淨現金流入（流出）','投資活動之淨現金流入（流出）', '融資or籌資活動之淨現金流入（流出）']
                    print(pd_combine.to_markdown())
                
                # 合併損益:
                elif 'ajax_t51sb13' in fa:
                    report = report[1:-1]
                    for i in range(len(report)):
                        report[i].columns = report[i].columns.get_level_values(0)  
                    for r in report: # 因為列表裡面很多 '公司代號' 跟 數字 塞在一起, 所以先清乾淨
                        indexNames = r[ r['公司代號'] == '公司代號' ].index
                        r.drop(indexNames , inplace=True)
                        r['公司代號'] = r['公司代號'].astype('int64')
                    report = [i.set_index('公司代號') for i in report]

                    for i in report:
                        if int(stocks) in i.index:
                            got = i.loc[int(stocks)]
                            got = got.to_frame().T
                            print(got.to_markdown())
                            break
        
    return 

def call_by_year(stocks):
    YEAR_List_Before101 = [97]
    for year in YEAR_List_Before101:
        _ = call_FinancialAccountingList(year, stocks)
    YEAR_List_After101 = [109]
    for year in YEAR_List_After101:
        _ = call_FinancialAccountingList(year, stocks)
    return 
############################################  [TEST Done]   ########################################################

def go_stock(stocks):
    _ = call_by_year(stocks)
    return 


# go_stock(2330)
go_stock(2880)
# go_stock(2317)
# go_stock(2379)
# go_stock(9955)


#%%

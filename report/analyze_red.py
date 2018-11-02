from pandas import DataFrame, Series
import pandas as pd
import numpy as np
from query_historical_data import historical_data
from census import census_data
debug = 0
class analyze_red:
    def get_red_matrix_df (self):
        h_data = historical_data()
        rs=h_data.get_all_data()
        return DataFrame(census_data.get_red_matrix(rs))

    def get_indexed_red_matrix(self,red_matrix_frame):
        df= red_matrix_frame.loc[:,[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33]].cumsum()
        df[34]=red_matrix_frame[0]
        df['index']=df.index
        return df

    def get_historical_rounds(self,df):
        s=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        length= len(df)
        result=[]
        maxV=[]
        for i in range (length):
            rs = df.loc[i,[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33]].sub(s)
            if rs.min(axis=0)>0:
                s = df.loc[i]
                result.append(i)
                maxV.append(rs.max(axis=0))

        resultLen=[]
        length= len(result) 
        for i in range (length): 
            if i==0: resultLen.append(result[0]) 
            else: resultLen.append(result[i]-result[i-1])

        dfResult=DataFrame(result)
        dfResult['max']=maxV 
        dfResult['length']=resultLen 
        return dfResult

    def get_historical_rounds_describe(self,dfResult):
        return dfResult[(dfResult['max']>3) & (dfResult['max'] <15)].describe()

    def SumCurrentCol (self,df):
        return df.loc[:,[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33]].cumsum()
    def GetRedSumFrame(self,df,startRow,endRow):
        return self.SumCurrentCol(df.iloc[startRow:endRow])

    def get_current_red_frame(self,red_matrix,start,end):
        return self.GetRedSumFrame(red_matrix,start,end)

if __name__ == "__main__":
    analyzer = analyze_red()

    if debug == 1: print ('===start===')
    
    red_matrix_frame = analyzer.get_red_matrix_df ()

    df_indexed =  analyzer.get_indexed_red_matrix(red_matrix_frame)
    
    red_matrix_len =len(df_indexed)
    
    df_r = analyzer.get_historical_rounds (df_indexed)
    
    start = df_r.loc[len(df_r)-1,0].astype(int)+1

    if debug == 1: print (df_r.values.tolist())
    
    df_r_des = analyzer.get_historical_rounds_describe(df_r)
    
    ls_des= [[]]
    ls_title =['count','mean','std','min','25%','50%','75%','max']
    i=0
    for ls in df_r_des.values.tolist():
        ls.append(ls_title[i])
        i=i+1
        ls_des.append(ls)
    if debug == 1: print (ls_des)
    
    current_red= analyzer.get_current_red_frame(red_matrix_frame,start,red_matrix_len)
    
    if debug == 1: print(current_red.values.tolist())  
    if debug == 1: print ('===end===')
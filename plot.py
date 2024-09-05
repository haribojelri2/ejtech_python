from scipy.stats import linregress
import pandas as pd
import numpy as np
np.seterr(invalid='ignore')


class Graph():
    def __init__(self, df, start_date, end_date, predict_date, timeInterval=1):
        self.df = df
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.rawSettlement = self.df['침하량']
        self.predictData = self.df[(self.df['측정일'] >= self.start_date) & (self.df['측정일'] <= self.end_date)]
        self.t = (self.predictData['측정일'] - self.start_date).dt.days
        self.settlement = self.predictData['침하량']
        self.so = self.settlement.iloc[0]
        self.sl = self.settlement.iloc[-1]
        self.s_diff = self.settlement - self.so
        self.date_pred = pd.date_range(start=self.start_date, end=self.end_date + pd.Timedelta(days=int(predict_date)), freq='D')
        self.date = self.df[self.df['측정일'] < self.end_date]
        self.timeInterval = int(timeInterval) if timeInterval else 1
    def basic_plot(self):
        return self.df['측정일'], self.df['성토고']
        
    def hyperbolic_plot(self):
        t_s = (-self.t[1:] / self.s_diff[1:])
        b, a, _, _, _ = linregress(self.t[1:], t_s)
        s_final = 1 / b - self.so
        t_pred = (self.date_pred - self.start_date).days
        s_pred = self.so - t_pred / (a + b * t_pred)

        # Convert dates to lists
        date_pred_list = list(self.date_pred)
        date_measurement_list = list(self.date['측정일'])

        # Combine dates and sort
        combined_dates = sorted(set(date_pred_list) | set(date_measurement_list))

        # Prepare s_pred to match combined_dates length
        s_pred_dict = dict(zip(date_pred_list, s_pred))
        s_pred_combined = [s_pred_dict.get(date, None) for date in combined_dates]

        # Adjust rawSettlement to match combined_dates length
        raw_settlement_dict = dict(zip(self.date['측정일'], self.rawSettlement))
        raw_settlement_combined = [raw_settlement_dict.get(date, None) for date in combined_dates]
        return combined_dates, s_pred_combined, raw_settlement_combined, self.t[1:], t_s, a + b * self.t[1:] ,t_pred, self.so,a,b,s_final,self.sl

    def hosino_plot(self):
        t_s = (self.t[1:]/(self.s_diff[1:])**2)
        b, a, _, _, _ = linregress(self.t[1:], t_s)
        s_final = np.sqrt(1 / b) - self.so
        if np.isnan(s_final):
            s_final = None
        t_pred = (self.date_pred - self.start_date).days
        s_pred = self.so - np.sqrt(t_pred / (a + b * t_pred))
        s_pred = [None if np.isnan(value) else value for value in s_pred]

        
        date_pred_list = list(self.date_pred)
        date_measurement_list = list(self.date['측정일'])
        
        # Combine dates and sort
        combined_dates = sorted(set(date_pred_list) | set(date_measurement_list))
        s_pred_dict = dict(zip(date_pred_list, s_pred))
        s_pred_combined = [s_pred_dict.get(date, None) for date in combined_dates]

        raw_settlement_dict = dict(zip(self.date['측정일'], self.rawSettlement))
        raw_settlement_combined = [raw_settlement_dict.get(date, None) for date in combined_dates]

        return combined_dates, s_pred_combined, raw_settlement_combined, self.t[1:], t_s, a + b * self.t[1:] ,t_pred, self.so,a,b,s_final,self.sl

    def asaoka_plot(self):
        date_range = pd.date_range(start=self.df['측정일'].min(), end=self.df['측정일'].max(), freq='D')
        existing_dates = set(self.df['측정일'])
        complete_dates = set(date_range)
        missing_dates = complete_dates - existing_dates

        missing_dates_df = pd.DataFrame(sorted(missing_dates), columns=['측정일'])
        combined_df = pd.concat([self.df, missing_dates_df]).sort_values(by='측정일').reset_index(drop=True)

        combined_df['침하량'] = combined_df['침하량'].interpolate(method='linear')
        combined_df = combined_df[(combined_df['측정일']>=self.start_date) & (combined_df['측정일']<=self.end_date)]

        data=combined_df['침하량'].iloc[::self.timeInterval]
        s1 = data[:-1]
        s2 = data[1:]
        b, a, _, _, _ = linregress(s1*-1, s2*-1)
        s_final = a/(1-b)*-1
        t_pred = (self.date_pred - self.start_date).days
        s_pred = s_final -(s_final-s1.iloc[0]) * np.exp(t_pred[1:] * np.log(b)/self.timeInterval)
        date_pred_list = list(self.date_pred)
        date_measurement_list = list(self.date['측정일'])
        
        combined_dates = sorted(set(date_pred_list) | set(date_measurement_list))
        indices_to_keep = set(range(0, len(s_pred), self.timeInterval))

        s_pred = [s_pred[i] if i in indices_to_keep else None for i in range(len(s_pred))]
        s_pred_dict = dict(zip(date_pred_list, s_pred))
        s_pred_combined = [s_pred_dict.get(date, None) for date in combined_dates]

        raw_settlement_dict = dict(zip(self.date['측정일'], self.rawSettlement))
        raw_settlement_combined = [raw_settlement_dict.get(date, None) for date in combined_dates]
        x_cross = a /(1-b)
        y_cross = x_cross 
        x_min = min(s1*-1)
        x_max = max(max(s1*-1), x_cross)*1.05
        x_range = np.linspace(x_min, x_max)

        return combined_dates ,s_pred_combined , raw_settlement_combined, self.so, a,b,s_final, self.timeInterval , x_cross, y_cross, x_range.tolist(), x_min,x_max,t_pred,s1,self.sl,combined_df['측정일'].iloc[::self.timeInterval].tolist(),combined_df['침하량'].iloc[::self.timeInterval].tolist()
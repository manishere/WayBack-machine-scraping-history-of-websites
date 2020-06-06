import requests
import json
import timestamp_convertor as convertor  

class TimestampManager:

    GET_YEARS_URL_START = "https://web.archive.org/__wb/sparkline?output=json&url="
    GET_YEARS_URL_END   = "&collection=web&output=json"           #URL COMES BETWEEN START AND END

    GET_TS_URL_START = "https://web.archive.org/__wb/calendarcaptures?url="
    GET_TS_URL_END   =  "&selected_year="

    ARCHIVE_URL = "https://web.archive.org/web/"

    
    def __init__(self, url, initial_ts=None):
        self._prev = False
        self._url = url
        #print(self._get_ts_data(2011))
        self._years = self._get_years_data()
        if initial_ts is None:
            self._current_year = self._years[0]
            self._ts_data = {self._current_year: self._get_ts_data(self._current_year)}
            self._current = self._ts_data[self._current_year][0]
        else:
            self._ts_data = {}
            self.set_current(str(initial_ts))
        #print(self._current)        


    def set_current(self, ts):
        tm = convertor.ts_to_time(str(ts))   
        if str(tm.tm_year) not in self._years:
            raise Exception("Invalid Timestamp")     
        self._current_year = str(tm.tm_year)
        self._current = ts
        self._refresh()


    def current(self):
        return self._current


    def next(self):   
        curr_data = self._ts_data[self._current_year]
        index = curr_data.index(self._current)  
        if index == len(curr_data) - 1:
            if self._current_year == self._years[-1]: 
                return 
            else:
                curr_year_index = self._years.index(self._current_year)
                self._current_year = self._years[curr_year_index + 1]   
                self._current = None
                self._prev = False   
                self._refresh()  
        else:
            self._current = curr_data[index + 1]


    def prev(self):   
        curr_data = self._ts_data[self._current_year]
        index = curr_data.index(self._current)
        if index == 0:
            if self._current_year == self._years[0]: 
                return 
            else:
                curr_year_index = self._years.index(self._current_year)
                self._current_year = self._years[curr_year_index - 1]   
                self._current = None
                self._prev = True
                self._refresh()  
        else:
            self._current = curr_data[index - 1]


    def first(self):  
        return self._first_ts


    def last(self):   
        return self._last_ts    


    def scrap(self):  
        url = self.ARCHIVE_URL + self._current + "/" + self._url
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception('Unable to connect to archive.org')

        return response.content


    def _refresh(self):
        if self._current_year in self._ts_data:
            data = self._ts_data[self._current_year]
        else:
            data = self._get_ts_data(self._current_year)
            self._ts_data[self._current_year] = data
        
        if self._current is None:           
            if self._prev:                      
                self._current = data[-1]         
            else:
                self._current = data[0]          
            return                          
        for ts in data:
            if int(self._current) <= int(ts):      
                self._current = str(ts)
                return
        self._current = data[-1]                


    def _get_years_data(self):
        data = self._get_raw_years_data()
        self._first_ts = data['first_ts']
        self._last_ts = data['last_ts']
        return sorted([str(k) for k in data['years'].keys()])     
    
    
    def _get_ts_data(self, year):
        data = self._get_raw_ts_data(year)
        ts_array = []
        for month in data:
            for week in month:
                for day in week:
                    if day is None or 'ts' not in day:
                        continue
                    for ts in day['ts']:
                        ts_array.append(str(ts))
        return sorted(ts_array)                

   
    def _get_raw_years_data(self):
        url = self.GET_YEARS_URL_START + self._url + self.GET_YEARS_URL_END  
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception("Unable to get years data")

        return json.loads(response.content)


    def _get_raw_ts_data(self, year):
        url = self.GET_TS_URL_START + self._url + self.GET_TS_URL_END + str(year) 
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception("Unable to get timestamp data")

        return json.loads(response.content)



if __name__ == "__main__":
    manager = TimestampManager(url="DESIRED URL WHICH HAS TIMESTAMPS",)        
    temp = manager.current()
    print(temp)
    manager.next()

    while temp != manager.current():
        print(manager.current())
        temp = manager.current()
        manager.next()
    
    #print(manager.current())
    #manager.next()
    #print(manager.current())


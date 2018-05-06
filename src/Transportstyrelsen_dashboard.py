
# coding: utf-8

# In[17]:


from datetime import datetime
import tkinter.messagebox as messagebox
import tkinter as tk
from tkinter import ttk
import requests, json, io
import pandas as pd
import webbrowser
import pylab
import matplotlib.pyplot as plt
from matplotlib.pyplot import style
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
style.use('seaborn')

class TS_dashboard(tk.Tk):
    
    def __init__(self,parent):
        tk.Tk.__init__(self,parent)        
        tk.Tk.configure(self,background='white') # App bg color
        tk.Tk.geometry(self,"800x600") # Set window size
        tk.Tk.wm_title(self,'Transportstyrelsen statistics') # Window title
        tk.Tk.iconbitmap(self,r'pictures/ts_logo_cut.ico') # Window icon
        self.parent = parent
        self.initialize_app()
        self.currentYear = datetime.now().year
        self.resizable(False, False)
        
        # Top dropdown
        top_menu = tk.Menu(self)
        self.config(menu=top_menu)
        file_menu = tk.Menu(top_menu, tearoff=0)
        top_menu.add_cascade(label="File",menu=file_menu)
        file_menu.add_command(label="About", command=lambda: [messagebox.showinfo("About", "Application developed by Alexander Röstberg. Version 1.0.")])
        file_menu.add_command(label="Exit", command=lambda: [self.destroy()])
     
    # To open TS link
    def ts_link(eventa,eventb): 
        webbrowser.open_new(r"http://transportstyrelsen.se")
    
    # Get the API status
    def get_status(self):
        url = 'http://tsopendata.azure-api.net/Vagtrafikolyckor/v0.13/Olycksniva'
        r = requests.get(url)
        state = r.status_code
        
        return state
    
    # Retrieve monthly statistics from Transportstyrelsen API
    def accidents_month(self,startYear,endYear): 
        months = list(range(1,13))
        years_m = list(range(startYear,endYear+1)) # Monthly plots for these years
        
        #API initial query
        payload = {
            '$count': "true"
        }
        
        #API Connect
        url = 'http://tsopendata.azure-api.net/Vagtrafikolyckor/v0.13/Olycksniva'
        
        stat_cont_yearmonth = {}

        # Loop through the months
        try:
            for i in years_m:
                stat_cont_yearmonth[i] = {}
                for m in months:
                    payload['$filter'] = "Ar eq {} and Manad eq {} and Svarighetsgrad eq 'Dödsolycka'".format(i,m)
                    r = requests.get(url, params=payload)
                    result_json = r.json()
                    data = result_json['@odata.count']
                    stat_cont_yearmonth[i][m] = data

        except Exception as e:
            print('Response code: ', r.status_code) # Write status code and error upon exception
            print(e)

        df_month_year = pd.DataFrame.from_dict(stat_cont_yearmonth, orient='columns')

        return df_month_year
    
    # Retrieve yearly statistics from Transportstyrelsen API
    def accidents_year(self,startYear,endYear): 
        
        years = list(range(startYear,endYear+1))
        
        #API initial query
        payload = {
            '$count': "true"
        }
        
                #API Connect URL
        url = 'http://tsopendata.azure-api.net/Vagtrafikolyckor/v0.13/Olycksniva'
        
        stat_cont_year = []
        date_cont_year = []

        #Loop through the years and append to lists
        try:
            for i in years:
                payload['$filter'] = "Ar eq {} and Svarighetsgrad eq 'Dödsolycka'".format(i)
                r = requests.get(url, params=payload)
                result_json = r.json()
                data = result_json['@odata.count']
                stat_cont_year.append(data)
                date_cont_year.append(i)

        except Exception as e:
            print('Response code: ', r.status_code) #Write status code and error upon exception
            print(e)

        df_year = pd.DataFrame(list(zip(date_cont_year, stat_cont_year)), columns=['Year','Fatal accidents'])
        df_year.set_index('Year', inplace=True)

        return df_year
    
    # ------------------------------- G U I ------------------------------- #
    
    # Startpage
    def initialize_app(self): 
        self.startPage = tk.Frame(self, bg='white', width=750, height=500)
        self.startPage.grid_rowconfigure(5, weight=1)
        self.startPage.grid_columnconfigure(5,weight=1)
        self.startPage.pack()
        
        # Logotype
        logo_ts = tk.PhotoImage(file=r'pictures/TS.PNG')
        logo_ts_label = tk.Label(self.startPage,image=logo_ts)
        logo_ts_label.image = logo_ts
        logo_ts_label.config(background = 'white')
        
        # Welcome text
        welcome = tk.Label(self.startPage, text="A service that retrieves fatal road accidents data from the Swedish Transport Agency")
        welcome.config(background = 'white')
        
        # TS link
        welcome2 = tk.Label(self.startPage, text="http://transportstyrelsen.se", fg="blue", cursor="hand2")
        welcome2.bind("<Button-1>", self.ts_link)
        welcome2.config(background = 'white')
        
        # Separator
        separate_it = ttk.Separator(self.startPage, orient=tk.HORIZONTAL)
        
        # Radio buttons
        self.radio_retrieve = tk.IntVar()
        
        yearly_radio_lab = tk.Label(self.startPage, text="Yearly statistics", bg='white')
        yearly_radio = tk.Radiobutton(self.startPage, variable=self.radio_retrieve,value=2, bg='white')
        
        monthly_radio_lab = tk.Label(self.startPage, text="Monthly statistics", bg='white')
        monthly_radio = tk.Radiobutton(self.startPage, variable=self.radio_retrieve,value=1, bg='white')
        
        # Start date label
        st_year_lab = tk.Label(self.startPage, text="Start date: ")
        st_year_lab.config(background = 'white')
        
        # Start date form
        maxValue = tk.IntVar()
        self.form_start = tk.Entry(self.startPage,background="white", textvariable=maxValue)
        
        # End year label
        end_year_lab = tk.Label(self.startPage, text="End date: ")
        end_year_lab.config(background = 'white')
        
        # End year form
        maxValue2 = tk.IntVar()
        self.form_end = tk.Entry(self.startPage, background="white", textvariable=maxValue2)
        
        # Generate button
        button_submit_years = tk.Button(self.startPage, background="#005BBB", width=15, text="Generate", command=self.dataPage)     
        
        # API status
        api_output = self.get_status() # Get response code
        
        if api_output == 200:
            api_status = tk.Label(self.startPage, bg='white',text='API connection: Established', pady=20) # Get status
            api_status_pic = tk.PhotoImage(file=r'pictures/connected.png')
        else:
            api_status = tk.Label(self.startPage, bg='white',text='API status: Not established', pady=20) # Get status
            api_status_pic = tk.PhotoImage(file=r'pictures/disconnected.png')
        
        api_status_pic_label = tk.Label(self.startPage, image=api_status_pic, background="white")
        api_status_pic.image = api_status_pic
        
        # Grids
        logo_ts_label.grid(row=1,column=0, columnspan=2)
        welcome.grid(row=2,column=0, columnspan=2)
        welcome2.grid(row=3,column=0, columnspan=2, pady=8)
        
        #Separator
        separate_it.grid(row=4, columnspan=10, sticky=tk.EW)
        
        # Radio buttons
        monthly_radio.grid(row=5,column=0, sticky=tk.E)
        monthly_radio_lab.grid(row=5,column=1, sticky=tk.W)
        yearly_radio.grid(row=6,column=0, sticky=tk.E)
        yearly_radio_lab.grid(row=6,column=1, sticky=tk.W)

        # Forms
        st_year_lab.grid(row=7,column=0, sticky=tk.E)
        end_year_lab.grid(row=8,column=0, sticky=tk.E)
        self.form_start.grid(row=7,column=1, sticky=tk.W)
        self.form_end.grid(row=8,column=1, sticky=tk.W)
        button_submit_years.grid(row=10,column=1, sticky=tk.W)
        
        # API status
        api_status.grid(row=11,column=1, sticky=tk.W)
        api_status_pic_label.grid(row=11,column=0, sticky=tk.E)
        
    # Monthly-plot-page
    def dataPage(self): 
        
        data_selection = int(self.radio_retrieve.get())
        start_data = int(self.form_start.get())
        end_data = int(self.form_end.get())
        
        # Validate input from user
        if start_data < 2003 or start_data > self.currentYear:
            messagebox.showerror("Incorrect value", "Only values between 2003 and {} are permitted".format(self.currentYear))
        elif end_data < start_data:
            messagebox.showerror("Incorrect value", "End year must be higher than start year")
        elif end_data > self.currentYear: 
            messagebox.showerror("Incorrect value", "End year cant be bigger than {}".format(self.currentYear))
        elif data_selection == 0:
            messagebox.showerror("Missing selection","Need to select yearly or monthly statistics")
        
        else:
            if data_selection == 1: # Display monthly data
                data = self.accidents_month(start_data,end_data) # Get DF
                self.startPage.destroy() # Destroy startpage
                
                dataPage = tk.Frame(self, bg='white')
                dataPage.grid_rowconfigure(2, weight=0)
                dataPage.grid_columnconfigure(2,weight=0)
                dataPage.grid(row=0,column=0)

                # Return button
                button_home = tk.Button(dataPage, background="#005BBB", width=15, text="Back", command=lambda: 
                                        [canvas.get_tk_widget().destroy(),dataPage.destroy(), self.initialize_app()]) 
                button_home.pack()

                # Plot matplotlib 
                f = Figure(figsize=(6,5), dpi=100)
                plot_month = f.add_subplot(111)
                plot_month.plot(data)
                plot_month.legend(data.columns.values)  
                plot_month.set_xticks(range(1,13)) # Set x-axis to disply the 12months
                plot_month.set_title('Fatal accidents per month {} - {}'.format(start_data,end_data))

                canvas = FigureCanvasTkAgg(f,self)
                canvas.show()
                canvas.get_tk_widget().grid(row=1,column=1)
                
            elif data_selection == 2: # Get yearly data
                data = self.accidents_year(start_data,end_data) # Get DF
                self.startPage.destroy() # Destroy startpage

                dataPage = tk.Frame(self, bg='white')
                dataPage.grid_rowconfigure(2, weight=0)
                dataPage.grid_columnconfigure(2,weight=0)
                dataPage.grid(row=0,column=0)

                # Return button
                button_home = tk.Button(dataPage, background="#005BBB", width=15, text="Back", command=lambda: 
                                        [canvas.get_tk_widget().destroy(),dataPage.destroy(), self.initialize_app()]) 
                button_home.pack()

                # Plot matplotlib 
                f = Figure(figsize=(6,5), dpi=100)
                plot_year = f.add_subplot(111)
                plot_year.plot(data)
                plot_year.legend(data.columns.values)
                plot_year.set_title('Fatal accidents per year {} - {}'.format(start_data,end_data))

                canvas = FigureCanvasTkAgg(f,self)
                canvas.show()
                canvas.get_tk_widget().grid(row=1,column=1)
        

app = TS_dashboard(None)
app.mainloop()


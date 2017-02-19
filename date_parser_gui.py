from tkinter import *
import pickle, os, datetime, json
from file_parser import *
#from file_mover import find_files, parse, move

ALL = N+S+W+E

class Application(Frame):
    '''
    A simple GUI interface to facilitate the transfer of files,
    last source path and target path are pickled and used to autofill their
    respective fields
    '''
    def __init__(self, master=None):
        '''
        Create a FileParser object. Retrieve pickled search summary data,
        if any and update parse_id to loaded value.
        '''
        Frame.__init__(self, master, bg = 'snow3',
                       highlightthickness =4,
                       highlightbackground = 'grey')
     
        self.master.rowconfigure(0, weight = 1)
        self.master.columnconfigure(0, weight = 1)
        self.master.bind('<Return>', self.run)
        self.grid(sticky = W+E+S+N)
        self.parser = FileParser()
        self.record_file = os.path.join(os.getcwd(), 'data\\records.pkl') 
        self.records = self.get_record(self.record_file)
        try:
            searchNumber = self.records['parse_id']
            self.parser.PARSE_ID = self.parse_id = searchNumber
            self.data_summary = self.records['search history']
        except:
            self.parse_id = self.parser.PARSE_ID
            self.data_summary = self.parser.SUMMARY
        self.createWidgets()
        
    def createWidgets(self):
        '''Create and add widgets to 'master' frame'''
        for r in range(20):
            self.rowconfigure(r, weight = 1)
        for  c in range(3):
            self.columnconfigure(c, weight = 1)

        #Centralized Color definitions
        bg = 'snow3'
        fg = 'black'
        line = 'white'

        #Extension
        self.extension = Frame(self, bg = bg, padx = 2, pady = 2)
        self.extension_entry = Entry(self.extension)
        self.extension_entry.pack()
        self.extension_entry.focus()
        self.extension_label = Label(self.extension,
                                      text = "Extensions\n",
                                      bg = bg,
                                      fg = fg)
        
        self.extension_label.pack(side = LEFT)
        self.extension.grid(row = 1, column = 0, sticky = W)

        #Source Path
        self.path = Frame(self, bg = bg, padx = 2, pady = 2)
        self.path_entry = Entry(self.path,width = 35)
        self.path_entry.pack()
        self.path_label = Label(self.path,
                                text = 'From Path or Drive\n',
                                bg = bg,
                                fg = fg)
        self.path_label.pack(side = LEFT)
        self.path.grid(row = 5, column = 0, sticky = W)
        
        #check for stored source path
        try:
            last_source = self.records['last_source']
            self.path_entry.insert(0, last_source)
        except TypeError:
            pass
           
        #Transfer to path
        self.target = Frame(self, bg = bg, padx = 2, pady = 2)
        self.target_entry = Entry(self.target,width = 35)
        self.target_entry.pack()
        self.target_label = Label(self.target, 
                                  text = 'path\\to\store\\file\n',
                                  bg = bg,
                                  fg = fg)
        self.target_label.pack(side = LEFT)
        self.target.grid(row = 6, column = 0, sticky = W)
        #Check for stored target path
        try:
            last_target = self.records['last_target']
            self.target_entry.insert(0, last_target)
        except TypeError:
            pass
        #min date
        self.mindate = Frame(self, bg = bg, padx = 2, pady = 2)
        self.mindate_entry = Entry(self.mindate)
        self.mindate_entry.pack()
        self.mindate_label = Label(self.mindate,
                                   text = 'From mm/dd/yyyy\n',
                                   bg = bg, 
                                   fg = fg)
        self.mindate_label.pack(side = LEFT)
        self.mindate.grid(row = 7, column = 0, sticky = W)
        #max date
        self.maxdate = Frame(self, bg = bg)
        self.maxdate_entry = Entry(self.maxdate)
        self.maxdate_entry.pack()
        self.maxdate_label = Label(self.maxdate,
                                   text = 'To mm/dd/yyyy\n',
                                   bg = bg, 
                                   fg = fg)
        self.maxdate_label.pack(side = LEFT)
        self.maxdate.grid(row = 7, column = 0, sticky = E)
        #visual line break
        self.line = Frame(self, bg = bg)
        self.line_label = Label(self.line, bg = bg,
                                fg = line,
                                text = '_________'*7).pack()
        self.line.grid(row = 8, columnspan = 2, column = 0,sticky = ALL)

        #taken/created/modified Filter
        #Filter by Label
        self.filter_label_frame = Frame(self, bg = bg)
        self.filter_label_frame.grid(row = 9, column = 0, sticky = W)
        self.filter_label = Label(self.filter_label_frame,
                                  text = 'Filter by:',
                                  bg = bg,
                                  fg = fg)
        self.filter_label.pack(side = LEFT)
        #Filter Checkboxes
        self.filter_by = Frame(self, bg = bg)
        self.filter_by.grid(row = 10, column = 0, sticky = W)
        self.taken_var = BooleanVar()
        self.created_var = BooleanVar()
        self.modified_var = BooleanVar()
        self.taken_var.set(True)
        
        #Date Taken
        self.taken = Checkbutton(self.filter_by, 
                              bg = bg,
                              fg = fg, 
                              text = 'Date Taken',
                              variable = self.taken_var,
                              onvalue = True,
                              offvalue = False).pack(side = LEFT)
        #Date Created
        self.created = Checkbutton(self.filter_by, 
                              bg = bg,
                              fg = fg, 
                              text = 'Date Created',
                              variable = self.created_var,
                              onvalue = True,
                              offvalue = False).pack(side = LEFT)
        #Date Modified
        self.modified = Checkbutton(self.filter_by,
                                    bg = bg,
                                    fg = fg,
                                    text = 'Date Modified',
                                    variable = self.modified_var,
                                    onvalue = True,
                                    offvalue = False).pack(side = LEFT)

        
        #visual line break
        self.second_line = Frame(self, bg = bg)
        self.second_line_label = Label(self.second_line, bg = bg,
                                fg = line,
                                text = '_________'*7).pack()
        self.second_line.grid(row = 12, columnspan = 2, column = 0,sticky = ALL)
        #Search Subdirectories or Parent Only
        #Walk Label
        self.search_label_frame = Frame(self, bg = bg)
        self.search_label_frame.grid(row = 11, column = 0, sticky = W)
        self.search_label = Label(self.search_label_frame,
                                  text = 'Search Subdirectories',
                                  bg = bg,
                                  fg = fg)
        #self.search_label.pack(side = LEFT)
        self.search_depth = Frame(self, bg = bg)
        self.search_depth.grid(row = 13, column = 0,sticky = W)
        self.search_var = BooleanVar()
        self.search_var.set(True)
        self.walk = Checkbutton(self.search_depth,
                                    bg = bg,
                                    fg = fg,
                                    text = 'Search Subdirectories',
                                    variable = self.search_var,
                                    onvalue = True,
                                    offvalue = False).pack(side = LEFT)
        #copy or cut/paste radiobuttons
        self.move = Frame(self, bg = bg)
        self.move.grid(row = 14, column = 0, sticky = W)

        self.but_var = IntVar()
        self.but_var.set(1)
        self.copy = Radiobutton(self.move,
                                    text = 'Copy Only',
                                    variable = self.but_var,
                                    value = 1,
                                    bg = bg,
                                    fg = fg)
        
        self.copy.pack(side = TOP)
        self.cut = Radiobutton(self.move,
                                   text = 'Cut/Paste',
                                   variable = self.but_var,
                                   value = 0,
                                   bg = bg,
                                   fg = fg)
        self.cut.pack(side = TOP)
        #final read out
        self.readout = Frame(self)
        self.read_label = Label(self.readout,
                                bg = bg,
                                fg = fg,
                                text = '')
        
        self.readout.grid(row = 19, column = 0)
        self.read_label.pack()
        #Submit button
        self.submit = Frame(self, bg = bg, padx = 2, pady = 2)
        self.submit.grid(row = 20, column = 0, columnspan = 2, sticky = E)
        self.sbutton = Button(self.submit,
                              bg = bg,
                              fg = fg,
                              width = 7,
                              text = 'Submit',
                              command = self.run)
        self.sbutton.pack(side = RIGHT)
        #Summary Display button
        self.summary = Frame(self, bg = bg, padx = 2, pady = 2)
        self.summary.grid(row = 20, column = 0, sticky = W)
        self.summary_display = Button(self.summary,
                                      bg = bg,
                                      fg = fg,
                                      text = 'Summary',
                                      command = self.summary_display)
        self.summary_display.pack(side = LEFT)
                                      
    
    def run(self, event = None):
        '''
        Run file_parse() from from file_parser module, serialize last path searched, last
        path files where saved to, and FileParse.PARSE_ID to autfill fields and track number
        searches performed.
        Display total number of files moved and mode used, more details available from
        summary winow.
        '''
        try:
            path, target = self.parser.file_parse(*self.get_entry())
            data = self.parser.SUMMARY
            self.data_summary.update(data)
            record = {'last_source'     : path,
                      'last_target'     : target,
                      'parse_id'        : self.parser.PARSE_ID,
                      'search history'  : self.data_summary,
                      }
            self.write_record(self.record_file, record)
            
            count = len(data[self.parse_id]["FILES"])
            self.parse_id = self.parser.PARSE_ID
            if self.but_var.get() == 1:
                self.read_label.configure(text = 'Copied %d files' % (count))
            elif self.but_var.get() == 0:
                self.read_label.configure(text = 'Cut/Paste %d files'% (count))
           # print(self.records['search history'].keys())
        except ValueError:
            pass
        
        
    def get_entry(self):
        values = []
        #self.sbutton.config(relief = SUNKEN)
        self.entries = [self.extension_entry,
                        self.path_entry,
                        self.target_entry,
                        self.mindate_entry,
                        self.maxdate_entry,
                        self.taken_var,
                        self.created_var,
                        self.modified_var,
                        self.search_var,
                        self.but_var]
        
        for entry in self.entries:
            values.append(entry.get())
       
        return values

    
    def write_record(self, fn, obj):
        with open(fn,'wb') as output:
            pickle.dump(obj, output)
    def get_record(self, fn):
        try:
            with open(fn, 'rb') as data:
                records = pickle.load(data)
            return records
        except FileNotFoundError:
            self.records = self.parser.SUMMARY

    def summary_display(self):
        bg = 'snow3'
        key = max(self.data_summary.keys())
        summary_window = Toplevel(bg = bg)
        summary_window.title('Summary')
        summary_frame = Frame(summary_window, bg = bg)
        summary_frame.pack(anchor = W)
        header = Label(summary_frame, bg = bg,text = 'Search  #{}'.format(key))
        header.pack()
        line_1 = Label(summary_frame,bg = bg, fg = 'white', text = '_'*31)
        line_1.pack()
        files = Label(summary_frame, bg = bg, text = 'Files   :  {}'.format(
            len(self.data_summary[key]['FILES'])))
        files.pack(anchor = W)
        time = Label(summary_frame, bg = bg, text = 'Time  :  {}'.format(
            self.data_summary[key]['TIME']))
        time.pack(anchor = W)
        mode = Label(summary_frame, bg = bg, text = 'Mode :  {}'.format(
            self.data_summary[key]['MODE']))
        mode.pack(anchor = W)
        line_2 = Label(summary_frame, bg = bg, fg = 'white', text = '_'*31)
        line_2.pack()
        ext_count_label = Label(summary_frame, bg = bg, text = 'Extension Count')
        ext_count_label.pack()
        count_output = ''
        for ext, count in self.data_summary[key]['EXT_COUNT'].items():
            count_output += '{}  : {}\n'.format(ext, count)
        ext_count = Label(summary_frame, bg = bg, text = count_output)
        ext_count.pack(anchor = W)


           
        
        


root = Tk()
root.title("Parse by Date 3.1")
app = Application(master=root)
app.mainloop()

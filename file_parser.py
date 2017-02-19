import os, sys, shutil
from datetime import datetime
from PIL import Image

class FileParser:
    def __init__(self):
        self.PARSE_ID = 100
        self.SUMMARY = {self.PARSE_ID: {'MODE': '',
                                        'TIME': None,
                                        'FILES': [],
                                        'EXT_COUNT':{}}}
    def file_parse(self, *args):
        #Track speed of search
        start = datetime.now()
        #Create a new dict entry for each search performed from
        #same FileParse object
        
        if self.PARSE_ID not in self.SUMMARY.keys():
            self.SUMMARY[self.PARSE_ID] = {'MODE': '',
                                           'TIME': None,
                                           'FILES': [],
                                           'EXT_COUNT':{}}
        
        extensions, source_directory, save_to,\
        min_date, max_date,\
        taken, created, modified,\
        walk, copy_paste = args
        FILTER_BY = (taken, created, modified)
        #If No max_date provided, set equal to min_date; search that date ONLY
        if max_date == '':
            max_date = min_date
        #convert date string to datetime.date()
        DATE_FORMAT = '%m/%d/%Y'
        MIN_DATE = datetime.strptime(min_date, DATE_FORMAT).date()
        MAX_DATE = datetime.strptime(max_date, DATE_FORMAT).date()
        if copy_paste == 0:
            cut = True
            copy = False
            self.track('MODE', 'Cut/Paste')
        else:
            cut = False
            copy = True
            self.track('MODE','Copy/Paste')
        #generate a list of lowercase extensions to match against
        extensions = [ext.lower().strip() for ext in extensions.split(',')]
        
        if not os.path.isdir(source_directory):
            raise AttributeError('Invalid Source Path Provided')
        if not os.path.isdir(save_to):
            os.mkdir(save_to)
        #Track file count, displayed to user after parsing is complete
        if walk:
            print('WALKING')
            #Traverse all subdirectories looking for specified file types
            walk = os.walk(source_directory)
            for block in walk:
                root, dir, files = block
                if root == save_to:
                    pass
                else:
                    for F in files:
                        fn, ext =  os.path.splitext(F)
                        #for ext in extensions:
                        if ext.lower() in extensions or extensions == ['*.*']:
                            fn = os.path.join(root, F)
                            if fn in os.listdir(save_to):
                                pass
                            else:
                                TIME_FRAME = self.compare_time(fn,
                                                               MIN_DATE,
                                                               MAX_DATE,
                                                               FILTER_BY)
                                if TIME_FRAME:
                                    self.move(fn,
                                              save_to,
                                              copy = copy,
                                              cut = cut)
                                else:
                                    pass
        else:
            #Search only top level directory
            files = [os.path.join(os.path.join(source_directory, fn)) \
                     for fn in os.listdir(source_directory)\
                     if os.path.isfile(os.path.join(source_directory,fn))]
            for F in files:
                fn, ext = os.path.splitext(F)
                if ext.lower() in extensions or extensions == ['*.*']:
                    if os.path.basename(F) in os.listdir(save_to):
                        pass
                    else:
                        TIME_FRAME = self.compare_time(F,
                                                       MIN_DATE,
                                                       MAX_DATE,
                                                       FILTER_BY)
                        
                        if TIME_FRAME:
                            self.move(F, save_to, copy = copy, cut = cut)
                        else:
                            pass

        #Close Speed test
        end = datetime.now()
        self.track('TIME', str(end-start))
        #Increment self.Parse_ID to allow multiple file searches with single
        #FileParser object
        self.PARSE_ID += 1
        return source_directory, save_to

                        
    def compare_time(self, file, min_date, max_date, filter_by):
        '''
        Compare an images Exif 'Taken On', created, and/or modified Dates to a
        range set by the min_date - max_date args.  Only one date being compared
        needs to fall within range for function to return True. Files without
        known 'Taken Dates' acceptable, but won't be matched by that parameter.
        '''
        DATE_FORMAT = '%m/%d/%Y'
        TIME_FORMAT ='%a %b %d %H:%M:%S %Y'
        #Place Holders for respective dates
        FILTER_TAKEN = None
        FILTER_CREATED = None
        FILTER_MODIFIED = None
        #Parameters to filter by
        taken, created, modified  = filter_by
        
        #Only check files dates if not already cleared to cut/copy
        if file not in self.SUMMARY[self.PARSE_ID]['FILES']:
            if taken:
                try:
                    #Get Date Orginally Taken from exif info
                    image = Image.open(
                            file)._getexif()[36867].split()[0].split(':')
                    
                    FILTER_TAKEN = datetime.strptime(
                                    "/".join(image), '%Y/%m/%d').date()    
                except:
                    pass
                
            if created:
                #get file creation date
                FILTER_CREATED = os.path.getctime(file)
                FILTER_CREATED = datetime.strptime(
                datetime.fromtimestamp(FILTER_CREATED).strftime(
                DATE_FORMAT), DATE_FORMAT).date()

            if modified:
                #get date file last modified
                FILTER_MODIFIED = os.path.getmtime(file)
                FILTER_MODIFIED = datetime.strptime(
                datetime.fromtimestamp(FILTER_MODIFIED).strftime(
                DATE_FORMAT), DATE_FORMAT).date()
                
            for filter_date in (FILTER_TAKEN, FILTER_CREATED, FILTER_MODIFIED):
                #If filter date falls within provided date range, return True
                #if no filter_date returns True, return False
                try:
                    if min_date <= filter_date <= max_date:

                        return True
                    else:
                        pass
                except TypeError:
                    pass
            return False
                
    def move(self, file, target, copy = False, cut = False):
        '''
        Transfer file to target location, create target directory if 
        directory does not exist.
        '''
        if os.path.basename(file) not in os.listdir(target):
            if copy:
                try:
                    
                    shutil.copy(file, target)
                    self.track('FILES', file, target)
                    self.track('EXT_COUNT', file)
               
                except:
                    pass
                
            elif cut:
                try:
                    shutil.move(file, target)
                    self.track('FILES', file, target)
                    self.track('EXT_COUNT', file)
                except:
                    pass

    def track(self, key, value, *args):
        log = self.SUMMARY
        ID = self.PARSE_ID
        if key in ('MODE','TIME'):
            log[ID][key] = value
            
        if key == 'FILES':
            target, = args
            fn = os.path.basename(value)
            if fn not in log[ID][key]:
                log[ID][key].append(fn)      
               
        if key == 'EXT_COUNT':
            fn, ext = os.path.splitext(value)
            if ext not in log[ID][key].keys():
                log[ID][key][ext] = 1
            else:
                log[ID][key][ext] += 1
        
if __name__ == "__main__":
    
    Parser = FileParser()
    path = os.getcwd()
    file = 'testImage.JPG'


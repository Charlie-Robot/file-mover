import unittest, os, tempfile, shutil
from time import gmtime, strftime
from file_parser import *


class Test(unittest.TestCase):
    def setUp(self):
        
        #Testfiles
        self.IMG = 'testImage.JPG'
        self.TXT = 'testText.txt'
        self.BMP = 'testBMP.bmp'
        #Define Directories to use
        self.PATH = os.path.join(os.getcwd(), 'Test Files')
        self.TARGET_PATH_1 = tempfile.mkdtemp(dir = os.getcwd())
        self.TARGET_PATH_2 = tempfile.mkdtemp(dir = self.TARGET_PATH_1)
        self.TARGET_PATH_3 = tempfile.mkdtemp(dir = self.TARGET_PATH_1)
        #FileParser object
        self.PARSER = FileParser()
        #Search Parameters to test
        #Date Range string to pass file_parse()
        self.EARLIEST = '02/11/2016'
        self.LATEST = '02/18/2016'
        #Date Range Date object to pass to compare_time()
        #==>file_parse() handles conversion before calliing compare_time()
        self.EARLIEST_DATE = datetime.strptime('01/01/2016', '%m/%d/%Y').date()
        self.LATEST_DATE = datetime.strptime('02/28/2016', '%m/%d/%Y').date()
        #Date Filters
        self.TAKEN = (True, False, False)
        self.CREATED = (False, True, False)
        self.MODIFIED = (False, False, True)
        self.TAKEN_OR_CREATED = (True, True, False)
        self.TAKEN_OR_MODIFIED = (True, False, True)
        self.CREATED_OR_MODIFIED = (False, True, True)
        self.ANY_MATCH = (True, True, True)
    
    def test_compare_time_taken(self):
        self.IMG = os.path.join(self.PATH, self.IMG)
        self.assertTrue(self.PARSER.compare_time(self.IMG,
                                                 self.EARLIEST_DATE,
                                                 self.LATEST_DATE,
                                                 self.TAKEN))
        
    def test_compare_time_created(self):
        self.IMG = os.path.join(self.PATH, self.IMG)
        self.assertFalse(self.PARSER.compare_time(self.IMG,
                                                 self.EARLIEST_DATE,
                                                 self.LATEST_DATE,
                                                 self.CREATED))
    def test_compare_time_modified(self):
        self.IMG = os.path.join(self.PATH, self.IMG)
        self.assertTrue(self.PARSER.compare_time(self.IMG,
                                                 self.EARLIEST_DATE,
                                                 self.LATEST_DATE,
                                                 self.MODIFIED))
    def test_compare_time_taken_or_modified(self):
        self.IMG = os.path.join(self.PATH, self.IMG)
        self.assertTrue(self.PARSER.compare_time(self.IMG,
                                                 self.EARLIEST_DATE,
                                                 self.LATEST_DATE,
                                                 self.TAKEN_OR_MODIFIED))
    def test_compare_time_taken_or_created(self):
        self.IMG = os.path.join(self.PATH, self.IMG)
        self.assertTrue(self.PARSER.compare_time(self.IMG,
                                                 self.EARLIEST_DATE,
                                                 self.LATEST_DATE,
                                                 self.TAKEN_OR_CREATED))
    
    def test_compare_time_created_or_modified(self):
        self.IMG = os.path.join(self.PATH, self.IMG)
        self.assertTrue(self.PARSER.compare_time(self.IMG,
                                                 self.EARLIEST_DATE,
                                                 self.LATEST_DATE,
                                                 self.CREATED_OR_MODIFIED))
    
    def test_move(self):
        '''
        Test both copy/paste and cut/paste functionality, in order to leave
        images known parameters in tact for testing, first image is copied to
        new temp folder, then cut/paste to a second temp folder, leaving
        original inplace and unaltered.
        '''

        FILE = os.path.join(self.PATH, self.IMG)
        #Test Copy/Paste 
        self.assertTrue(os.path.isdir(self.TARGET_PATH_1))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_1))
        self.assertTrue(self.IMG in os.listdir(self.PATH))
        
        #...Copy the FILE to self.TARGET_PATH_1
        self.PARSER.move(FILE, self.TARGET_PATH_1, copy = True)
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_1))
        self.assertTrue(self.IMG in os.listdir(self.PATH))

        #Test Cut/Paste 
        FILE = os.path.join(self.TARGET_PATH_1, self.IMG)
        self.TARGET_PATH_2 = tempfile.mkdtemp(dir = self.TARGET_PATH_1)
        self.assertTrue(os.path.isdir(self.TARGET_PATH_2))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_2))

        #...Cut/Paste FILE to self.TARGET_PATH_2
        self.PARSER.move(FILE, self.TARGET_PATH_2, cut = True)
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_2))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_1))

    def test_make_new_directory(self):
        '''
        If destination directory DOES NOT EXIST, create it, then move files
        to newly created directory
        '''
        TARGET_PATH_4 = os.path.join(self.TARGET_PATH_1, 'new_dir_1')
        TARGET_PATH_5 = os.path.join(self.TARGET_PATH_2, 'new_dir_2')
        self.assertFalse(os.path.isdir(TARGET_PATH_4))
        self.assertFalse(os.path.isdir(TARGET_PATH_5))
        #Check that new directory is created with copy/paste, no subdirectory search
        self.PARSER.file_parse('.jpg, .py',
                               self.PATH, TARGET_PATH_4,
                               self.EARLIEST,
                               self.LATEST,
                               True, True, True, False, True)
        self.assertTrue(os.path.isdir(TARGET_PATH_4))
        self.assertTrue(self.IMG in os.listdir(TARGET_PATH_4))
        #Check that new directory is created with cupt/paset no subdirectories
        self.PARSER.file_parse('.jpg',
                               TARGET_PATH_4, TARGET_PATH_5,
                               self.EARLIEST, self.LATEST,
                               True, True, True, False, False)
        self.assertTrue(os.path.isdir(TARGET_PATH_5))
        self.assertFalse(self.IMG in os.listdir(TARGET_PATH_4))
        self.assertTrue(self.IMG in os.listdir(TARGET_PATH_5))
        #Check directory creation with subdirectory search, cut/paste
        shutil.rmtree(TARGET_PATH_4)
        self.assertFalse(os.path.isdir(TARGET_PATH_4))
        self.PARSER.file_parse('.jpg',
                               self.TARGET_PATH_1, TARGET_PATH_4,
                               self.EARLIEST, self.LATEST,
                               True, True, True, True, False)
        self.assertTrue(self.IMG in os.listdir(TARGET_PATH_4))
        #Check directory creation with subdirectory search, copy/paste
        shutil.rmtree(TARGET_PATH_5)
        self.assertFalse(os.path.isdir(TARGET_PATH_5))
        self.PARSER.file_parse('.jpg',
                               self.TARGET_PATH_1, TARGET_PATH_5,
                               self.EARLIEST, self.LATEST,
                               True, True, True, True, True)
        self.assertTrue(self.IMG in os.listdir(TARGET_PATH_5))
        
        
        
        
        
        
        
          
    def test_file_tracking(self):
        '''
        FileParse object should track what files where moved, how many of what
        extension type was moved, and if they where copy/paste OR cut/paste.
        Creates a new PARSE_ID and new dict for each search performed. Should
        NOT Track files iterated over that match search parameters but ARE NOT
        moved i.e: if destination folder already has a file by that name.
        '''
        #FileParser should instantiate with
        #MOVED = {PARSE_ID: {'MODE':'', 'TIME': None, 'FILES':[], 'EXT_COUNT':{}}}
        self.assertIsInstance(self.PARSER.SUMMARY, dict)
        self.assertEqual(len(self.PARSER.SUMMARY[100].keys()), 4)
        for k in ('MODE', 'TIME', 'FILES', 'EXT_COUNT'):
            self.assertTrue(k in self.PARSER.SUMMARY[100].keys())
        self.assertIsInstance(
            self.PARSER.SUMMARY[self.PARSER.PARSE_ID], dict)
        self.assertIsInstance(
            self.PARSER.SUMMARY[self.PARSER.PARSE_ID]['MODE'], str)
        self.assertEqual(
            self.PARSER.SUMMARY[self.PARSER.PARSE_ID]['MODE'],'' )
        self.assertIsInstance(
            self.PARSER.SUMMARY[self.PARSER.PARSE_ID]['TIME'], type(None))
        self.assertIsInstance(
            self.PARSER.SUMMARY[self.PARSER.PARSE_ID]["FILES"], list)
        self.assertEqual(
            len(self.PARSER.SUMMARY[self.PARSER.PARSE_ID]['FILES']), 0)
        self.assertIsInstance(
            self.PARSER.SUMMARY[self.PARSER.PARSE_ID]['EXT_COUNT'], dict)
        self.assertEqual(
            len(self.PARSER.SUMMARY[self.PARSER.PARSE_ID]['EXT_COUNT']), 0)
        self.assertEqual(self.PARSER.PARSE_ID, 100)

        #Run file_parse() No Subdirectories, Copy/Paste
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_1))
        self.PARSER.file_parse('.jpg, .py',
                               self.PATH, self.TARGET_PATH_1,
                               self.EARLIEST,
                               self.LATEST,
                               True, True, True, False, True)        
        self.assertEqual(
            self.PARSER.PARSE_ID, 101)
        self.assertEqual(
            self.PARSER.SUMMARY[100]['MODE'], 'Copy/Paste')
        self.assertEqual(
            self.PARSER.SUMMARY[100]['FILES'], ['testImage.JPG'])
        self.assertEqual(
            self.PARSER.SUMMARY[100]['EXT_COUNT'], {'.JPG': 1})
        self.assertIsInstance(
            self.PARSER.SUMMARY[100]['TIME'], str)
        self.assertNotEqual(
            self.PARSER.SUMMARY[100]['TIME'], '0:00:00.000000') 
        self.assertTrue(self.IMG in os.listdir(self.PATH))
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_1))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_2))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_3))

        #Run second search from same FileParse object
        #No subdirectories, Cut/paste
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_2))
        self.PARSER.file_parse('.jpg',
                               self.TARGET_PATH_1, self.TARGET_PATH_2,
                               self.EARLIEST, self.LATEST,
                               True, True, True, False, False)
        
        self.assertEqual(len(self.PARSER.SUMMARY[101].keys()), 4)
        for k in ('MODE', 'TIME', 'FILES', 'EXT_COUNT'):
            self.assertTrue(k in self.PARSER.SUMMARY[101].keys())
        
        self.assertEqual(
            self.PARSER.PARSE_ID, 102)
        self.assertEqual(
            self.PARSER.SUMMARY[101]['MODE'], 'Cut/Paste')
        self.assertEqual(
            self.PARSER.SUMMARY[101]['FILES'], ['testImage.JPG'])
        self.assertEqual(
            self.PARSER.SUMMARY[101]['EXT_COUNT'], {'.JPG': 1})
        self.assertIsInstance(
            self.PARSER.SUMMARY[101]['TIME'], str)
        self.assertNotEqual(
            self.PARSER.SUMMARY[101]['TIME'], '0:00:00.000000') 
        self.assertTrue(self.IMG in os.listdir(self.PATH))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_1))
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_2))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_3))

        #Run third search from same FileParse object,
        #with subdirectories, Copy/paste
        #files should not be tracked if TARGET_PATH already has a copy of file
        #being parsed
        self.assertTrue(self.IMG in os.listdir(self.PATH))
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_2))
        self.PARSER.file_parse('.jpg',
                               self.PATH, self.TARGET_PATH_2,
                               self.EARLIEST, self.LATEST,
                               True, True, True, True, True)
        
        self.assertEqual(
            self.PARSER.PARSE_ID, 103)
        self.assertEqual(
            self.PARSER.SUMMARY[102]['MODE'], 'Copy/Paste')
        self.assertEqual(
            self.PARSER.SUMMARY[102]['FILES'], [])
        self.assertEqual(
            self.PARSER.SUMMARY[102]['EXT_COUNT'], {})
        self.assertTrue(self.IMG in os.listdir(self.PATH))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_1))
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_2))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_3))
        self.assertEqual(['testImage.JPG'], os.listdir(self.TARGET_PATH_2))

        #Run fourth search from same FileParse object,
        #with subdirectories, Cut/paste to empty
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_2))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_3))
        self.PARSER.file_parse('.jpg',
                               self.TARGET_PATH_2, self.TARGET_PATH_3,
                               self.EARLIEST, self.LATEST,
                               True, True, True, True, False)
  
        self.assertEqual(
            self.PARSER.PARSE_ID, 104)
        self.assertEqual(
            self.PARSER.SUMMARY[103]['MODE'], 'Cut/Paste')
        self.assertEqual(
            self.PARSER.SUMMARY[103]['FILES'], ['testImage.JPG'])
        self.assertEqual(
            self.PARSER.SUMMARY[103]['EXT_COUNT'], {'.JPG': 1})
        self.assertTrue(self.IMG in os.listdir(self.PATH))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_1))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_2))
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_3))
        

        #Run fifth search from same FileParse object,
        #with subdirectories, Cut/paste
        #If file being parsed already in TARGET_PATH, file should not be tracked
        #in SUMMARY, and file should remain in place
        #Check that Cut/paste doesn't track/modify already existing files
        self.assertTrue(self.IMG in os.listdir(self.PATH))
        self.PARSER.file_parse('.jpg',
                               self.TARGET_PATH_3, self.PATH,
                               self.EARLIEST, self.LATEST,
                               True, True, True, True, False)

        self.assertEqual(
            self.PARSER.PARSE_ID, 105)
        self.assertEqual(
            self.PARSER.SUMMARY[104]['MODE'], 'Cut/Paste')
        self.assertEqual(
            self.PARSER.SUMMARY[104]['FILES'], [])
        self.assertEqual(
            self.PARSER.SUMMARY[104]['EXT_COUNT'], {})
        self.assertTrue(self.IMG in os.listdir(self.PATH))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_1))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_2))
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_3))

        #Sixth search, same Filearse object, check that Copy/paste does not
        #Track already exisitng files
        self.PARSER.file_parse('.jpg',
                               self.TARGET_PATH_3, self.PATH,
                               self.EARLIEST, self.LATEST,
                               True, True, True, True, False)
 
        self.assertEqual(
            self.PARSER.PARSE_ID, 106)
        self.assertEqual(
            self.PARSER.SUMMARY[105]['MODE'], 'Cut/Paste')
        self.assertEqual(
            self.PARSER.SUMMARY[105]['FILES'], [])
        self.assertEqual(
            self.PARSER.SUMMARY[105]['EXT_COUNT'], {})
        self.assertTrue(self.IMG in os.listdir(self.PATH))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_1))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_2))
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_3))

    
    def test_subdirectory_search(self):
        self.assertTrue(self.IMG in os.listdir(self.PATH))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_2))
        self.PARSER.file_parse('.jpg',
                              self.PATH,self.TARGET_PATH_2,
                              self.EARLIEST, self.LATEST,
                              True,True,True,False,True)
        self.assertTrue(self.IMG in os.listdir(self.PATH))
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_2))
        
        #Start search from an directory that DOES NOT CONTAIN ANY FILES, but
        #DOES CONTAIN OTHER DIRECTORIES, one of the subdirectories contains
        #the control file, the other subdirectory is empty.
        self.assertTrue(os.path.basename(self.TARGET_PATH_2) in
                        os.listdir(self.TARGET_PATH_1))
        self.assertTrue(os.path.basename(self.TARGET_PATH_3) in
                        os.listdir(self.TARGET_PATH_1))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_1))
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_2))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_3))
        #Cut/Paste from TARGET_PATH_2 to TARGET_PATH_3
        self.PARSER.file_parse('.jpg',
                              self.TARGET_PATH_1,self.TARGET_PATH_3,
                              self.EARLIEST, self.LATEST,
                              True,True,True,True,False)
        self.assertTrue(self.IMG in os.listdir(self.PATH))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_1))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_2))
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_3))

        #Copy/Paste from TARGET_PATH_3 to TARGET_PATH_1, bringing it
        #from subdirectory up to parent directory level
        self.PARSER.file_parse('.jpg',
                               self.TARGET_PATH_1, self.TARGET_PATH_1,
                               self.EARLIEST, self.LATEST,
                               True, True, True, True, True)
       
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_1))
        self.assertFalse(self.IMG in os.listdir(self.TARGET_PATH_2))
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_3))

    def test_extension_case(self):
        #Test that user can enter extensions in any case format and file_parse
        #will return any case form of those extensions.
 
        self.assertTrue(self.IMG in os.listdir(self.PATH))
      
        EXPECTED_EXTENSION = os.path.splitext(self.IMG)[1]
        #Check lowercase user input
        self.assertNotEqual('.jpg', EXPECTED_EXTENSION)
        self.PARSER.file_parse('.jpg',
                               self.PATH, self.TARGET_PATH_1,
                               self.EARLIEST, self.LATEST,
                               True, True, True, False, True)
        #Test that file extension was not altered to reflect user case usage
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_1))
        self.assertFalse('testImage.jpg' in os.listdir(self.TARGET_PATH_1))

        #Check mixed case user input
        self.assertNotEqual('.Jpg', EXPECTED_EXTENSION)
        self.PARSER.file_parse('.jpg',
                               self.PATH, self.TARGET_PATH_1,
                               self.EARLIEST, self.LATEST,
                               True, True, True, False, True)
        #Test that file extension was not altered to reflect user case usage
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_1))
        self.assertFalse('testImage.Jpg' in os.listdir(self.TARGET_PATH_1))

    def test_file_type(self):
        TODAY = strftime('%m/%d/%Y', gmtime())
        #Test that non image files don't throw errors if 'Taken by' parameter is
        #True i.e, '.jpg, .txt' will check .jpg's Taken on date but .txt will pass
        #without mention
        self.assertTrue(self.IMG not in os.listdir(self.TARGET_PATH_1))
        self.assertTrue(self.TXT not in os.listdir(self.TARGET_PATH_1))
        self.PARSER.file_parse('.jpg, .txt',
                               self.PATH, self.TARGET_PATH_1,
                               self.EARLIEST, TODAY,
                               True, False, False, False, True)
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_1))
        self.assertTrue(self.TXT not in os.listdir(self.TARGET_PATH_1))

    def test_find_all_files(self):
        #Test that if user uses '*.*' as extension arg, ALL files matching
        #filter_by parameters are returned regardless of what extension they have
        TODAY = strftime('%m/%d/%Y', gmtime())
        self.assertTrue('testImage.JPG' in os.listdir(self.PATH))
        self.assertTrue('testText.txt' in os.listdir(self.PATH))
        self.assertTrue('testBMP.bmp' in os.listdir(self.PATH))
        self.PARSER.file_parse('*.*',
                               self.PATH, self.TARGET_PATH_1,
                               self.EARLIEST, TODAY,
                               True, True, True, False, True)
        self.assertTrue('testImage.JPG' in os.listdir(self.TARGET_PATH_1))
        self.assertTrue('testText.txt' in os.listdir(self.TARGET_PATH_1))
        self.assertTrue('testBMP.bmp' in os.listdir(self.TARGET_PATH_1))
        self.assertTrue('testImage.JPG' not in os.listdir(self.TARGET_PATH_2))
        self.assertTrue('testText.txt' not in os.listdir(self.TARGET_PATH_2))
        self.assertTrue('testBMP.bmp' not in os.listdir(self.TARGET_PATH_2))
        self.PARSER.file_parse('*.*',
                               self.TARGET_PATH_1, self.TARGET_PATH_2,
                               self.EARLIEST, TODAY,
                               False, True, False, False, True)       
        self.assertTrue('testImage.JPG' in os.listdir(self.TARGET_PATH_2))
        self.assertTrue('testText.txt' in os.listdir(self.TARGET_PATH_2))
        self.assertTrue('testBMP.bmp' in os.listdir(self.TARGET_PATH_2))
        self.assertTrue('testImage.JPG' not in os.listdir(self.TARGET_PATH_3))
        self.assertTrue('testText.txt' not in os.listdir(self.TARGET_PATH_3))
        self.assertTrue('testBMP.bmp' not in os.listdir(self.TARGET_PATH_3))
        self.PARSER.file_parse('*.*',
                               self.TARGET_PATH_2, self.TARGET_PATH_3,
                               self.EARLIEST, TODAY,
                               False, False, True, False, True)
        self.assertTrue('testImage.JPG' in os.listdir(self.TARGET_PATH_3))
        self.assertTrue('testText.txt' in os.listdir(self.TARGET_PATH_3))
        self.assertTrue('testBMP.bmp' in os.listdir(self.TARGET_PATH_3))
        
        
    def test_filter_by_mode(self):
        #Test Taken By, Created On, and Modified filters
        TODAY = strftime('%m/%d/%Y', gmtime())
        self.assertTrue('testImage.JPG' in os.listdir(self.PATH))
        self.assertTrue('testText.txt' in os.listdir(self.PATH))
        self.assertTrue('testBMP.bmp' in os.listdir(self.PATH))
        #CHECK Taken On
        #testImage.JPG taken outside of provided date range
        self.PARSER.file_parse('.jpg, .txt, .bmp',
                               self.PATH, self.TARGET_PATH_1,
                               self.LATEST, TODAY,
                               True, False, False, False, True)
        self.assertTrue('testImage.JPG' not in os.listdir(self.TARGET_PATH_1))
        self.assertTrue('testText.txt' not in os.listdir(self.TARGET_PATH_1))
        self.assertTrue('testBMP.bmp' not in os.listdir(self.TARGET_PATH_1))
        #testImage.JPG taken within provided date range
        self.assertTrue('testImage.JPG' in os.listdir(self.PATH))
        self.assertTrue('testText.txt' in os.listdir(self.PATH))
        self.assertTrue('testBMP.bmp' in os.listdir(self.PATH))
        self.PARSER.file_parse('.jpg, .txt, .bmp',
                               self.PATH, self.TARGET_PATH_1,
                               self.EARLIEST, TODAY,
                               True, False, False, False, True)
        self.assertTrue('testImage.JPG' in os.listdir(self.TARGET_PATH_1))
        self.assertTrue('testText.txt' not in os.listdir(self.TARGET_PATH_1))
        self.assertTrue('testBMP.bmp' not in os.listdir(self.TARGET_PATH_1))

        #CHECK Created On
        #No test files Created within provided date range
        self.assertTrue('testImage.JPG' in os.listdir(self.PATH))
        self.assertTrue('testText.txt' in os.listdir(self.PATH))
        self.assertTrue('testBMP.bmp' in os.listdir(self.PATH))
        self.PARSER.file_parse('.jpg, .txt, .bmp',
                               self.PATH, self.TARGET_PATH_2,
                               self.EARLIEST, self.LATEST,
                               False, True, False, False, True)
        self.assertTrue('testImage.JPG' not in os.listdir(self.TARGET_PATH_2))
        self.assertTrue('testText.txt' not in os.listdir(self.TARGET_PATH_2))
        self.assertTrue('testBMP.bmp' not in os.listdir(self.TARGET_PATH_2))
        #All test files Created within provided date range, 
        self.PARSER.file_parse('.txt ,.bmp',
                               self.PATH, self.TARGET_PATH_2,
                               self.EARLIEST, TODAY,
                               False, True, False, False, True)
        self.assertTrue('testImage.JPG' not in os.listdir(self.TARGET_PATH_2))
        self.assertTrue('testText.txt' in os.listdir(self.TARGET_PATH_2))
        self.assertTrue('testBMP.bmp' in os.listdir(self.TARGET_PATH_2))

        #CHECK Modified On
        #ALL  Copies of Test files have been modified TODAY, orignal
        #testImage.JPG has a modified date in the past
        self.assertTrue('testImage.JPG' in os.listdir(self.TARGET_PATH_1))
        self.assertTrue('testText.txt' not in os.listdir(self.TARGET_PATH_1))
        self.assertTrue('testBMP.bmp' not in os.listdir(self.TARGET_PATH_1))
        self.assertTrue('testImage.JPG' not in os.listdir(self.TARGET_PATH_2))
        self.assertTrue('testText.txt' in os.listdir(self.TARGET_PATH_2))
        self.assertTrue('testBMP.bmp' in os.listdir(self.TARGET_PATH_2))
        #Should Cut/paste all the copies made above and move them
        #to TARGET_PATH_3
        self.PARSER.file_parse('.jpg, .txt, .bmp',
                               self.TARGET_PATH_1, self.TARGET_PATH_3,
                               self.EARLIEST, TODAY,
                               False, False, True, True, False)
        self.assertTrue('testImage.JPG' not in os.listdir(self.TARGET_PATH_1))
        self.assertTrue('testText.txt' not in os.listdir(self.TARGET_PATH_1))
        self.assertTrue('testBMP.bmp' not in os.listdir(self.TARGET_PATH_1))
        self.assertTrue('testImage.JPG' not in os.listdir(self.TARGET_PATH_2))
        self.assertTrue('testText.txt' not in os.listdir(self.TARGET_PATH_2))
        self.assertTrue('testBMP.bmp' not in os.listdir(self.TARGET_PATH_2))
        self.assertTrue('testImage.JPG' in os.listdir(self.TARGET_PATH_3))
        self.assertTrue('testText.txt' in os.listdir(self.TARGET_PATH_3))
        self.assertTrue('testBMP.bmp' in os.listdir(self.TARGET_PATH_3))

        #Only make a copy of testImage.JPG
        self.assertTrue('testImage.JPG' in os.listdir(self.PATH))
        self.assertTrue('testText.txt' in os.listdir(self.PATH))
        self.assertTrue('testBMP.bmp' in os.listdir(self.PATH))
        self.PARSER.file_parse('.jpg, .txt, .bmp',
                               self.PATH, self.TARGET_PATH_1,
                               self.EARLIEST, self.LATEST,
                               False, False, True, False, True)
        self.assertTrue('testImage.JPG' in os.listdir(self.PATH))
        self.assertTrue('testImage.JPG' in os.listdir(self.TARGET_PATH_1))
        self.assertTrue('testText.txt' not in os.listdir(self.TARGET_PATH_1))
        self.assertTrue('testBMP.bmp' not in os.listdir(self.TARGET_PATH_1))

    def test_single_date_field__date_range(self):
        #If user only enters the early end of a date range, only that date is
        #searched => a date range of one day 01/11/2012 - 01/11/2012
        self.assertTrue(self.IMG in os.listdir(self.PATH))
        self.PARSER.file_parse('.jpg',
                               self.PATH, self.TARGET_PATH_1,
                               '02/11/2016', '',
                               True, False, False, False, True)
        self.assertTrue(self.IMG in os.listdir(self.PATH))
        self.assertTrue(self.IMG in os.listdir(self.TARGET_PATH_1))

            
    def tearDown(self):
        
        shutil.rmtree(self.TARGET_PATH_1)
    
        


if __name__ == '__main__':
    unittest.main()

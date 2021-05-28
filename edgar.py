from sec_edgar_downloader import Downloader
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))






# Initialize a downloader instance. If no argument is passed
# to the constructor, the package will download filings to
# the current working directory.
dl = Downloader(dir_path)

# Get all 10-Q filings for Visa
dl.get("10-Q", "CARV", amount=4)
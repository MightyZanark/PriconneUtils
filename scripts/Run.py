import sys
import multiprocessing
from DBCheck import update_db
from Movie import movie
from Sound import sound

def run_main():
    print("\n---------- Priconne Utilities ----------\n")
    print("> DBCheck: Checks if DB is up to date, recommended to do first time")
    print("> Movie: Downloads L2D, UB Cutin, or Summon animations depending on what you want")
    print("> Sound: Downloads BGMs and converts them from .wav to .m4a to save space")
    print("To choose what you want to do, just write 'DBCheck', 'Movie', or 'Sound'")
    
    while True:
        ans = input("\nChoose action: 'DBCheck' 'Movie' 'Sound\n")
        if str(ans).lower().strip() == 'dbcheck':
            print("'DBCheck' option chosen\n")
            update_db()
        
        elif str(ans).lower().strip() == 'movie':
            print("'Movie' option chosen\n")
            movie()
        
        elif str(ans).lower().strip() == 'sound':
            print("'Sound' option chosen\n")
            sound()
        
        else:
            print("> INVALID ACTION! <\nCurrently supported actions: 'DBCheck' 'Movie' 'Sound'")
            input("Press ENTER to continue\n")
        
        again = input("Do you want to do another action? (y/N)\n")
        if str(again).lower().strip() == 'y':
            continue
        else:
            break
    
    input("Press ENTER to exit this window")

if __name__ == '__main__':
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()
    run_main()
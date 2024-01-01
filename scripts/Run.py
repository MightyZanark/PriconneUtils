import sys
import multiprocessing
from .DBCheck import update_db
from .Movie import movie
from .Sound import sound

def run_main():
    print("\n---------- Priconne Utilities ----------\n")
    print("> DBCheck: Checks if DB is up to date, recommended to do first time")
    print("> Movie: Downloads L2D, UB Cutin, or Summon animations depending on what you want")
    print("> Sound: Downloads BGMs and converts them from .wav to .m4a to save space")
    print("To choose what you want to do, write 1 for 'DBCheck', 2 for 'Movie', or 3 for 'Sound'")
    
    while True:
        print("\nChoose action:")
        print("1. DBCheck\n2. Movie\n3. Sound")
        ans = input(">> ").lower().strip()
        if ans == '1':
            print("'DBCheck' option chosen\n")
            update_db()
        
        elif ans == '2':
            print("'Movie' option chosen\n")
            movie()
        
        elif ans == '3':
            print("'Sound' option chosen\n")
            sound()
        
        else:
            print("> INVALID ACTION! <\nCurrently supported actions: 'DBCheck' 'Movie' 'Sound'")
            input("Press ENTER to continue\n")
        
        again = input("Do you want to do another action? (y/N)\n").lower().strip()
        if again != 'y' or again[0] != 'y':
            break
    
    input("Press ENTER to exit this window")


if __name__ == '__main__':
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()
    
    run_main()

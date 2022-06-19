from DBCheck import update_db
from Movie import main as movie

def main():
    print("\n---------- Priconne Utilities ----------\n")
    print("> DBCheck: Checks if DB is up to date, recommended to do first time")
    print("> Movie: Downloads L2D, UB Cutin, or Summon animations depending on what you want")
    print("To choose what you want to do, just write 'DBCheck' or 'Movie'")
    
    ans = input("Choose action: 'DBCheck' 'Movie'\n")
    if str(ans).lower().strip() == 'dbcheck':
        print("'DBCheck' option chosen, checking and updating DB...\n")
        update_db()
        input("\nAll task is done!\nPress ENTER to exit this window")
    
    elif str(ans).lower().strip() == 'movie':
        print("'Movie' option chosen")
        movie()
    
    else:
        print("> INVALID ACTION! <\nCurrently supported actions: 'DBCheck' and 'Movie'")
        input("Press ENTER to exit this window")

if __name__ == '__main__':
    main()
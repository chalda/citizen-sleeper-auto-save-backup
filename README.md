Periodic backup script for Citizen Sleeper save data.  
Monitors a game save folder and creates timestamped backups when changes are detected.  
The game periodically overwrites the savegame files as you play that can be corrupted in case of a crash.  
Seemingly a common issue, with some players losing playthroughs dozens of hours into the game.  
If you click Continue and get an infinite loading screen, bad savefile is probably the reason.  
The default paths for different OSes are defined but but your milage may vary.  
Default save paths are defined but only tested on Windows, please report issues or alternative setups.  
Dont save scum, let the dice fall where they do.


### Features:
- checks save file location based on your OS, known defaults are defined below and can be modified if needed
 - creates a copy of the entire gamedata folder
 - copies are appended a timestamp and stored in a 'backups' folder local to the script
 - checks if savefile has been modified since last copy to avoid filling your drive if you left the script running
 - backup frequency can be configured below, defaults to 10 minutes

### Running:
No external deps, on most OSes should run with 
python ./backup_script.py
Windows users can now install python from the App Store and run the script with
py.exe .\backup_script.py
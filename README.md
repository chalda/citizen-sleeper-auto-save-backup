Periodic backup script for [Citizen Sleeper](https://store.steampowered.com/app/1578650/Citizen_Sleeper/) save data.  
Monitors a game save folder and creates timestamped backups when changes are detected.  
The game periodically overwrites the savegame files as you play that can be corrupted in case of a crash.  
Seemingly a common issue, with some players losing playthroughs dozens of hours into the game.  
If you click Continue and get an infinite loading screen, bad savefile is probably the reason.  
The default paths for different OSes are defined but but your milage may vary.  
Default save paths are defined but only tested on Windows, please report issues or alternative setups.  
Dont save scum, let the dice fall where they do.  
5/5 game  


### Features:
- checks save file location based on your OS, known defaults are defined below and can be modified if needed
 - creates a copy of the entire gamedata folder
 - copies are appended a timestamp and stored in a 'backups' folder local to the script
 - only copies the folder if any savefile has been modified since last backup to avoid filling your drive
 - backup frequency can be configured below, defaults to 10 minutes

### Running:
No external dependencies, so running should be simple on most OS:  
`python backup_script.py`

For Windows users, the current recommended way is now to install the Python app from the App Store.
Run the script in PowerShell with:  
`py.exe backup_script.py`
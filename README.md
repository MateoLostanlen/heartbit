# Install
```bash
pip install -r requierements.txt 
```


# Setup cron
```bash
*/5 * * * * cd /home/pi/heartbit && sudo /home/pi/heartbit/venv/bin/python get_heartbit.py >> /home/pi/heartbit/cron.log 2>&1
```

# Get file 
```bash
scp pi@192.168.1.56:heartbit/heartbit.json heartbit.json
```

# Run notebook to analyse evolution
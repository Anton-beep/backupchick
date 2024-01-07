# Setup (Dcoker)
```shell
git clone https://github.com/Anton-beep/backupchick
cd backupchick
docker build -t backupchick .
docker run -d --name backupchick -v <local dir to backup>:/usr/src/app/backupDir backupchick --telegram_token=<your telegram token> --backup_interval=<backup interval in seconds> --chat_password=<your chat password>  
```

You can check if bot is running by sending `%ping` command to it in Telegram.

To authorize in bot you need to send `%auth <your chat password>` command to it.

To check if you are authorized you need to send `%status` command to it.

To get backup you need to send `%get_backup` command to it. Bot will send backup by itself every `backup_interval` seconds. _(one hour is `3600` seconds, one day is `86400` seconds)_
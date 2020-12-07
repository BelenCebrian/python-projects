# Python3 projects 

What you will find here: short Python3 projects that I use everyday, sorted into folders. 

Mainly to monitor things and keep me informed using Telegram bots. 

And usually run in a Raspberry Pi device I have always on :)

## Webmonitor

>

## Speedmonitor

![]()

1. Do a speedtest every hour and log the results into a csv file (`speedmonitor.py`)

1. At a later time, make a graph and send it via Telegram's bot (`graph.py`). 

1. At last, a script to keep everything organized (`move.py`)

`cron` is used to launch the scripts at the appropiate time. For example, in case of `speedmonitor.py` the crontab file has this line (it means it's executed every hour):

```0 * * * * python3 $HOME/scripts/speedmonitor/speedmonitor.py &```
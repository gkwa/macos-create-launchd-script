# macos-create-launchd-script
1. run `./genscript.py` and output is a bunch of bash scripts
2. run the one you want 
```bash
ls -1 *.sh
bash net.taylorm.launcha.show-urls-for-recent-homebrews.sh
```
3. remind yourself how to use launchd with 
```bash
cat net.taylorm.launcha.show-urls-for-recent-homebrews.sh
```
4. run what you need, eg maybe 
```bash
launchctl unload $HOME/Library/LaunchAgents/net.taylorm.launcha.show-urls-for-recent-homebrews.plist
launchctl load $HOME/Library/LaunchAgents/net.taylorm.launcha.show-urls-for-recent-homebrews.plist
launchctl list | grep net.taylorm.launcha.show-urls-for-recent-homebrews
```

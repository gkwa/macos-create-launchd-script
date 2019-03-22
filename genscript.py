#!/usr/bin/env python

import sys

import yaml
from jinja2 import Template

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

tpl_logger = Template("""{# jinja2 -#}
/usr/bin/logger -is "Starting '$HOME/Library/Application Support/{{ label }}/{{ program }}' from $HOME/Library/LaunchAgents/{{ label }}.plist"
""")


tpl_installer = Template("""{# jinja2 -#}
#!/bin/bash

set -e

mkdir -p $HOME/Library/Logs/{{ label }}
mkdir -p "$HOME/Library/Application Support/{{ label }}"

cat <<__eot__ >"$HOME/Library/Application Support/{{ label }}/{{ program }}"
{{ script }}
__eot__

cat <<__eot__ >$HOME/Library/LaunchAgents/{{ label }}.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>

    <key>Label</key>
    <string>{{ label }}</string>

    <key>LowPriorityIO</key>
    <true/>

    <key>Program</key>
    <string>$HOME/Library/Application Support/{{ label }}/{{ program }}</string>

    <!-- great for debug since it runs as soon as we do launchctl load -->
    <key>RunAtLoad</key>
    <true/>

    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/{{ label }}/{{ label }}.err</string>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/{{ label }}/{{ label }}.out</string>

    <!-- lowest priority -->
    <key>Nice</key>
    <integer>19</integer>

    <key>StartInterval</key>
    <integer>{{ minute_frequency * 60 }}</integer>

  </dict>
</plist>
__eot__
chmod +x "$HOME/Library/Application Support/{{ label }}/{{ program }}"

# reminders for how to manipulate plsits and launchd
: <<COMMENTBLOCK
# debug
launchctl unload $HOME/Library/LaunchAgents/{{ label }}.plist
launchctl load $HOME/Library/LaunchAgents/{{ label }}.plist
launchctl list {{ label }}
launchctl list | grep {{ label }}
cat $HOME/Library/Logs/{{ label }}/{{ label }}.{err,out}
ls -la $HOME/Library/Logs/{{ label }}/*
ls -la $HOME/Library/LaunchAgents/{{ label }}.plist
launchctl unload $HOME/Library/LaunchAgents/{{ label }}.plist
cat "$HOME/Library/Application Support/{{ label }}/{{ program }}"
COMMENTBLOCK

# reminder for how to cleanup/abort this plist
: <<ABORT_UNLOAD_AND_CLEANUP
launchctl unload $HOME/Library/LaunchAgents/{{ label }}.plist
rm -f $HOME/Library/LaunchAgents/{{ label }}.plist
rm -rf "$HOME/Library/Logs/{{ label }}"
rm -rf "$HOME/Library/Application Support/{{ label }}"
ABORT_UNLOAD_AND_CLEANUP

""")

documents = """
---
label: net.taylorm.launcha.conditionally-pause-backblaze
program: pause-backup
minute_frequency: 15
script: |
 #!/bin/sh
 {{ logger }}
 ~/pdev/taylormonacelli/conditionally-pause-backblaze/pause-backup
---
label: net.taylorm.launcha.gcloudcomponentsupdate
program: updater
minute_frequency: 60
script: |
 #!/bin/sh
 {{ logger }}
 /usr/local/bin/gcloud components update --quiet
---
label: net.taylorm.launcha.testcron
program: touchit.sh
minute_frequency: 1
script: |
 #!/bin/sh
 {{ logger }}
 date >>/tmp/net.taylorm.launcha.testcron.log
"""

for dct in yaml.load_all(documents):
    tpl_script = Template(dct['script'])
    label = dct['label']
    genscript = "{}.sh".format(label)
    with open(genscript, 'w') as file_h:
        file_h.write(tpl_installer.render({ **dct, 'script' : tpl_script.render(logger=tpl_logger.render(dct)) }))

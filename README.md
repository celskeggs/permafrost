# Permafrost

This is a tool to facilitate making secure automated backups of parts of Qubes VMs, without having to back up the entire VM.

## Setting up template VM

    $ sudo apt install python3-gdbm

## Setting up permafrost VM

TODO

## Setting up a client VM

First, generate a new password in your password manager to encrypt this particular VM's backups.
(Make sure you have a backup of your password manager that isn't stored in your backups, to avoid a chicken-and-egg scenario.)

Copy the password you generated into /home/user/.permafrostkey in the VM you want to backup.

Next, you need to grant the appropriate permissions for the VM to automatically copy backup files around.
Edit `/etc/qubes-rpc/policy/qubes.Filecopy` in dom0 to add the following line:

    [YOURVM]	permafrost	allow

Make sure to add it before the `$anyvm	$anyvm	ask` line.

Now install the software:

    $ cd /home/user/
    $ git clone https://github.com/celskeggs/permafrost
    $ cd permafrost
    $ ./install-pfsave.sh

Confirm that the backups are running:

    $ systemctl status --user pfsave.service

It will take some time for this to work. You can monitor the progress with:

    $ sudo journalctl --follow

Though, again, it will take some time for the output to start showing up in any useful way.

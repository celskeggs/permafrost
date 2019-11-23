# Permafrost

This is a tool to facilitate making secure automated backups of parts of Qubes VMs, without having to back up the entire VM.

## Setting up template VM

    $ sudo apt install duplicity python3-gdbm python3-boto3

## Setting up permafrost VM

First, get a new Slack incoming webhook and paste the URL into `/home/user/.permafrostwebhook`.

Second, create a new S3 bucket and get an access key. Put the information into `/home/user/.permafrostremote` in the following JSON format:

    {
      "url": "<region url>",
      "bucket": "<name>",
      "key": "<key>",
      "secret": "<secret>"
    }

Third, install the software:

    $ cd /home/user/
    $ git clone https://github.com/celskeggs/permafrost
    $ cd permafrost
    $ ./install-pfaccept.sh
    $ ./install-pfupload.sh

Confirm that the services are running:

    $ systemctl status --user pfaccept.service
    $ systemctl status --user pfupload.service

Once you've installed a client VM, you should start seeing messages pop up reporting that the accept and upload scripts worked.

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

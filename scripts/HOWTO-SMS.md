# Bulk-sending of SMS

Tournament organisation is 10% orga and 90% dealing with people who do not read email. They just won't. To get them to actually absorb crucial information, such as the first game time, you are best sending text messages. This is one of the reasons that the [DrawMaker](https://github.com/madduck/tctools/tree/main/draw_maker) massages the data to get you a mobile number to use.

But now what? If you started texting everyone manually, your fingers will fall off. Therefore, I automated the sending. There are probably a number of services out there that provide you with the ability to send bulk messages. But my cell phone contract comes with unlimited messaging, and so I wanted to use that, for the additional benefit that I'd get replies and be able to interact with people even when I am not in front of my laptop.

If you want to do the same, there's a bit of work involved assembling the building blocks. Here is what you need:

* An Android phone — sorry iPhone folks.
* The [Project MAXS](http://projectmaxs.org/) family of apps, at least the [main app](https://f-droid.org/packages/org.projectmaxs.main/), the [XMPP transport](https://f-droid.org/packages/org.projectmaxs.transport.xmpp/), and the [SmsSend module](https://f-droid.org/packages/org.projectmaxs.module.smssend/).
* Two XMPP ("Jabber") accounts
* A Jabber client that's scriptable. I use [xmppc](https://codeberg.org/Anoxinon_e.V./xmppc).

MAXS is a suite of apps that allow you to remotely interact with your phone via XMPP, which is a chat protocol. Once configured, it will run on your phone and maintain a connection to a Jabber server, and allow a predefined correspondent to send you commands. This other, "predefined component" is what I configured for `xmppc`, and now I can just run:

```
% xmppc -m message chat myphone@madduck.net "sms send 021234567  Kia ora …"
```

and this will make my phone send a text message accordingly. It's really quite a cool project.

For tournament control, I use this in conjunction with the [player_mmerge](https://github.com/madduck/tctools/tree/main/scripts/player_mmerge.py) script:

```
./scripts/player_mmerge.py --drawmaker draw_maker.ods --waitlist --points 2100-2700 --gender f \
  'sms {number} Kia ora {first name}, this is Thorndon calling, we need you' \
  'to play our tournament. Are you keen? Let us know ASAP! -m ({squash code})'
```

This will only output the literal text, but I can append `| sh`, and the command will be executed in bulk. Beware, here be dragons, …

By the way, I always include their squash code in outgoing emails, which may be confusing, but which allows me to easily find correspondence in my SMS app.

Another example: after sending an email to all players using e.g. MailChimp, I want to send a reminder in case overzealous spam checkers are getting in the way again. However, there is no need to pester those people who have been recorded to have read the email. So, say you've exported a file with email addresses that have read your email to `/tmp/opened.csv`, you can now fire off:

```
./mmerge/player_mmerge.py dm.ods 'grep -qi "^{email}$" /tmp/opened.csv ||
echo "sms {number} Hi {first name}, the latest updates for the Sin City Open just went out via email (https://bit.ly/2Y1CXgv). If filed as spam, please teach your mailer. By now you should also be well aware of your draw and 1st game time (https://thorndonclub.co.nz/tc/live.html#{draw}). Looking forward to tomorrow/Friday! -m"'
```

And now append `| sh | sh` and it will only be sent to those who have not opened the message.

This is Linux-only, and I don't know how to make this run on Windows or Apple, but if you do, let's document it here. And also, please let me know if you want more information.

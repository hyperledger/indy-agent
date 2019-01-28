from indy import crypto, did, wallet
import asyncio
from os.path import expanduser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import os
import shutil
import zipfile


async def create():
    client = "test"
    wallet_config = '{"id": "%s-wallet"}' % client
    wallet_credentials = '{"key": "%s-wallet-key"}' % client
    opened = False

    # 1. Create Wallet and Get Wallet Handle
    try:
        await wallet.create_wallet(wallet_config, wallet_credentials)
        wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
        opened = True
        (my_did, my_vk) = await did.create_and_store_my_did(wallet_handle, "{}")
        print('my_did and verkey = %s %s' % (my_did, my_vk))
    except Exception as e:
        print("Wallet already created", e)
        pass
    if not opened:
        wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)

    print('wallet = %s' % wallet_handle)

    meta = await did.list_my_dids_with_meta(wallet_handle)
    print(meta)
    home = expanduser("~")
    filePath = home + '/.indy_client/wallet/test-wallet'
    # file = home + '/.indy_client/wallet/test-wallet'

    # zipf = zipfile.ZipFile('test-wallet.zip', 'w', zipfile.ZIP_DEFLATED)
    # for root, dirs, files in os.walk(filePath):
    #     for file in files:
    #         zipf.write(os.path.join(root, file))
    zipPath = shutil.make_archive('wallet', 'zip', filePath)
    return zipPath


def send(senderEmail, senderPwd, server, port, dest, fileName):
    '''$HOME/.indy_client/wallet/{id}/sqlite.db'''
    home = expanduser("~")
    # filepath = home + '/.indy_client/wallet/%s' % fileName
    # filename = fileName
    # attachment = open(filepath, "rb")
    attachment = open(fileName, "rb")

    # instance of MIMEMultipart
    m = MIMEMultipart()

        # attach the body with the msg instance
    m.attach(MIMEText('See attached file.', 'plain'))

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename=wallet.zip")

    # attach the instance 'p' to instance 'msg'
    m.attach(p)

    # storing the senders email address.
    m['From'] = senderEmail  # TODO: get from config

    # storing the receivers email address
    m['To'] = dest

    # storing the subject
    m['Subject'] = 'test-wallet'

    # creates SMTP session
    s = smtplib.SMTP(server, port)

    # start TLS for security
    s.starttls()

    # Authentication (If you use your personal email, use your personal password instread of 'I only talk via email!')
    s.login(senderEmail, senderPwd)

    # sending the mail
    s.sendmail(senderEmail, dest, m.as_string())

    # terminating the session
    s.quit()

def send_to_agent(zipPath):
    cfg = _configure()
    # print(cfg.sections)
    # for each_section in cfg.sections():
    #     for (each_key, each_val) in cfg.items(each_section):
    #         print (each_key)
    #         print (each_val)
    # args = _get_config_from_cmdline()
    # cfg = _get_config_from_file()
    # smtp_cfg = _apply_cfg(cfg, 'smtp2', _default_smtp_cfg)
    # imap_cfg = _apply_cfg(cfg, 'imap2', _default_imap_cfg)
    send(cfg['smtp2']['username'], cfg['smtp2']['password'], cfg['smtp2']['server'], cfg['smtp2']['port'], 'indyagent1@gmail.com', zipPath)

def _get_config_from_file():
    import configparser
    cfg = configparser.ConfigParser()
    home = expanduser("~")
    cfg_path = home + "/.mailagent/config.ini"
    # cfg.read('config.ini')
    if os.path.isfile(cfg_path):
        cfg.read(cfg_path)
    return cfg

def _configure():
    #args = _get_config_frm_cmdline()
    #_use_statefolder(args)
    cfg = _get_config_from_file()
    #ll = _get_loglevel(args)
    #_start_logging(ll)
    return cfg

#cfg = _configure()
#email_username = cfg['smtp2']['username']
#email_password = cfg['smtp2']['password']
loop = asyncio.get_event_loop()
zipPath = loop.run_until_complete(create())
send_to_agent(zipPath)

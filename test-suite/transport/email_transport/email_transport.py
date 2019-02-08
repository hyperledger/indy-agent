# Python code to illustrate Sending mail with json-format attachments
# from your Gmail account

# libraries to be imported
import smtplib
import os
import asyncio
import time
import logging

from indy import crypto, did, wallet

from os.path import expanduser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from .mail_handler import MailHandler

class SecureMsg():
    async def encryptMsg(self, msg):
        with open('plaintext.txt', 'w') as f:
            f.write(msg)
        with open('plaintext.txt', 'rb') as f:
            msg = f.read()
        print('msg is: ', msg)
        print('wallet_handle is: ', self.wallet_handle)
        print('my vk is: ', self.my_vk)
        print('their vk is: ', self.their_vk)
        encrypted = await crypto.auth_crypt(self.wallet_handle, self.my_vk, self.their_vk, msg)
        with open('encrypted.dat', 'wb') as f:
            f.write(bytes(encrypted))
        print('prepping %s' % msg)

#     # Step 6 code goes here, replacing the read() stub.
    async def decryptMsg(self, encrypted):
        decrypted = await crypto.auth_decrypt(self.wallet_handle, self.my_vk, encrypted)
        return (decrypted)
#
    async def init(self):
        me = 'Mailagent'.strip()
        self.wallet_config = '{"id": "%s-wallet"}' % me
        self.wallet_credentials = '{"key": "%s-wallet-key"}' % me
        # 1. Create Wallet and Get Wallet Handle
        try:
            await wallet.create_wallet(self.wallet_config, self.wallet_credentials)
        except:
            pass
        self.wallet_handle = await wallet.open_wallet(self.wallet_config, self.wallet_credentials)
        print('mailagent wallet = %s' % self.wallet_handle)

        (self.my_did, self.my_vk) = await did.create_and_store_my_did(self.wallet_handle, "{}")
        print("my_did", self.my_did)
        print("my_vk", self.my_vk)
        did_vk = {}
        did_vk["did"] = self.my_did
        did_vk["my_vk"] = self.my_vk
        self.their_did = ''
        self.their_vk = ''

    def __init__(self):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.init())
            time.sleep(1)  # waiting for libindy thread complete
        except KeyboardInterrupt:
            print('')

class EmailTransport():
    def __init__(self):
        self.smtp_cfg = _apply_cfg(cfg, 'smtp2', _default_smtp_cfg)
        self.imap_cfg = _apply_cfg(cfg, 'imap2', _default_imap_cfg)
        self.securemsg = SecureMsg()
        #creates a temp-wallet and adds their_vk to securemsg instance
        self.test_wallet = loop.run_until_complete(self.create())
        self.wallet_email_subject = "test-wallet"

    def send(self, senderEmail, senderPwd, server, port, dest, subject, raw_msg, filename):
        # instance of MIMEBase and named as p and To change the payload into encoded form
        p = MIMEBase('application', 'octet-stream')

        p.add_header('Content-Disposition', "attachment; filename=msg.ap")
        if filename != None:
            attachment = open(filename, "rb")
            p.set_payload((attachment).read())
        else:
            attachment = raw_msg
            p.set_payload((attachment))
        encoders.encode_base64(p)
        # instance of MIMEMultipart and attach the body with the msg instance
        m = MIMEMultipart()
        m.attach(MIMEText('See attached file.', 'plain'))

        # attach the instance 'p' to instance 'msg'
        m.attach(p)
        # storing the senders email info
        m['From'] = senderEmail  # TODO: get from config
        m['To'] = dest
        m['Subject'] = subject
        # creates SMTP session
        s = smtplib.SMTP(server, port)
        s.starttls()
        s.login(senderEmail, senderPwd)
        s.sendmail(senderEmail, dest, m.as_string())
        s.quit()

    def fetch_msg(self, trans, svr, ssl, username, password, their_email):
        return trans.receive(svr, ssl, username, password, their_email)

    def run(self, svr, ssl, username, password, their_email):
        incoming_email = None
        transport = None
        if not transport:
            transport = MailHandler()
        trans = transport
        logging.info('Agent started.')
        try:
            wc = self.fetch_msg(trans, svr, ssl, username, password, their_email)
            if wc:
                incoming_email = wc.msg
                print('incoming_email is:')
                print(incoming_email)
            else:
                time.sleep(2.0)
        except:
            logging.info('Agent stopped.')
        return incoming_email

    def send_to_agent(self, email_subject, raw_msg, filePath):
        self.send(self.smtp_cfg['username'], self.smtp_cfg['password'], self.smtp_cfg['server'], self.smtp_cfg['port'], 'indyagent1@gmail.com', email_subject, raw_msg, filePath)
        time.sleep(5.0)

    def send_encrypted_store_resp(self, encrypted_msg):
        self.send_to_agent("encrypted msg", encrypted_msg, None)
        return self.run(self.imap_cfg['server'], self.imap_cfg['ssl'], self.imap_cfg['username'], self.imap_cfg['password'], 'indyagent1@gmail.com')

    def send_wallet(self):
        self.send_to_agent(self.wallet_email_subject, None, self.test_wallet)
        os.remove(self.test_wallet)

    async def create(self):
        home = expanduser("~")
        filePath_create = home + '/.indy_client/wallet/testing'

        client = "test"
        wallet_config = '{"id": "%s-wallet", "storage_config": {"path":"%s"}}' % (client, filePath_create)
        wallet_credentials = '{"key": "%s-wallet-key"}' % client
        opened = False

        # 1. Create Wallet and Get Wallet Handle
        try:
            await wallet.create_wallet(wallet_config, wallet_credentials)
            wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
            opened = True
            # print("opened at try: ", opened)
            (their_did, their_vk) = await did.create_and_store_my_did(wallet_handle, "{}")
            # print('my_did and verkey = %s %s' % (their_did, their_vk))

        except Exception as e:
            print("Wallet already created", e)
            pass

        if not opened:
            wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
            (their_did, their_vk) = await did.create_and_store_my_did(wallet_handle, "{}")

        self.securemsg.their_did = their_did
        self.securemsg.their_vk = their_vk
        print("their_vk is: ", self.securemsg.their_vk)


        print('wallet = %s' % wallet_handle)

        filePath_export = home + '/.indy_client/wallet/exported-%s-wallet'%client
        export_config = '{ "path":"%s",  "key":"test-wallet-key"}' %(filePath_export)
        try:
            await wallet.export_wallet(wallet_handle, export_config)
        except Exception as e:
            if e.error_code == 'ErrorCode.CommonIOError':
                print("test-wallet already exported")
            pass
        await wallet.close_wallet(wallet_handle)

        await wallet.delete_wallet(wallet_config, wallet_credentials)

        return filePath_export

def _get_config_from_cmdline():
    import argparse
    parser = argparse.ArgumentParser(description="Run a Hyperledger Indy agent that communicates by email.")
    parser.add_argument("--ll", metavar='LVL', default="DEBUG", help="log level (default=INFO)")
    args = parser.parse_args()
    return args

def _get_config_from_file(home):
    import configparser
    cfg = configparser.ConfigParser()
    cfg_path = home+'/.mailagent/config.ini'
    if os.path.isfile(cfg_path):
        cfg.read(home+'/.mailagent/config.ini')
    return cfg

def _apply_cfg(cfg, section, defaults):
    x = defaults
    if cfg and (cfg[section]):
        src = cfg[section]
        for key in src:
            x[key] = src[key]
    return x

_default_smtp_cfg = {
    'server': 'smtp.gmail.com',
    'username': 'your email',
    'password': 'find the password from the config file',
    'port': '587'
}

_default_imap_cfg = {
    'server': 'imap.gmail.com',
    'username': 'indyagent1@gmail.com',
    'password': 'invalid password',
    'ssl': '1',
    'port': '993'
}

loop = asyncio.get_event_loop()
home = expanduser("~")
args = _get_config_from_cmdline()
cfg = _get_config_from_file(home)

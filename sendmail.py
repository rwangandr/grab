__author__ = 'rwang'

import smtplib
import email.MIMEMultipart
import email.MIMEText
import email.MIMEBase
import os.path



def sendmail(smtpserver, port, sender, subject, fromname, passwd, to, cc, mailbody, attachments=None):
    nRet = True
    if mailbody == "":
        print("The mailbody is empty")

    #
    main_msg = email.MIMEMultipart.MIMEMultipart()

    #
    text_msg = email.MIMEText.MIMEText(mailbody, 'html','utf-8')
    text_msg["Accept-Language"]="zh-CN"
    text_msg["Accept-Charset"]="ISO-8859-1,utf-8"
    main_msg.attach(text_msg)

    #
    contype = 'application/octet-stream'
    maintype, subtype = contype.split('/', 1)

    ##
    if attachments is not None:
        for attachment in attachments:
            # print attachment
            data = open(attachment, 'rb')
            file_msg = email.MIMEBase.MIMEBase(maintype, subtype)
            file_msg.set_payload(data.read())
            data.close()
            email.Encoders.encode_base64(file_msg)
            ##
            attachment = os.path.basename(attachment)
            # print attachment
            file_msg.add_header('Content-Disposition',
                                'attachment', filename=attachment)
            main_msg.attach(file_msg)

    #
    #main_msg['From'] = fromname
    main_msg['To'] = to

    main_msg['Subject'] = subject
    main_msg['Date'] = email.Utils.formatdate()
    toall = to
    if cc != '':
        main_msg['Cc'] = cc
        toall = to + "," + cc
    #
    fullText = main_msg.as_string()

    #
    server = None
    print ("setup mail connection")
    try:
        server = smtplib.SMTP(smtpserver, int(port))
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender, passwd)
        server.sendmail(sender, toall.split(","), fullText)
        print("Send email out")
    except smtplib.SMTPException:
#    except Exception, e:
        nRet = False
        print("Fail to send email")
    finally:
        if server:
            server.quit()
        return nRet


'''
def __rename_component(org_comp):
    new_comp = org_comp
    if org_comp.lower() == 'bmx':
        new_comp = 'sag'
    return new_comp
'''
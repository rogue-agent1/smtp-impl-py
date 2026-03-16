class SMTPMessage:
    def __init__(self,sender,recipients,subject,body):
        self.sender=sender;self.recipients=recipients;self.subject=subject;self.body=body
    def to_mime(self):
        headers=f"From: {self.sender}\r\nTo: {', '.join(self.recipients)}\r\nSubject: {self.subject}\r\n"
        headers+="MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\n"
        return headers+"\r\n"+self.body
class SMTPSession:
    def __init__(self): self.state='INIT';self.sender=None;self.recipients=[];self.data=None;self.log=[]
    def command(self,cmd):
        parts=cmd.split(' ',1); verb=parts[0].upper(); arg=parts[1] if len(parts)>1 else ''
        if verb=='EHLO': self.state='READY'; r=f"250 Hello {arg}"
        elif verb=='MAIL' and self.state=='READY':
            self.sender=arg.replace('FROM:','').strip('<>'); self.state='MAIL'; r="250 OK"
        elif verb=='RCPT' and self.state in ('MAIL','RCPT'):
            self.recipients.append(arg.replace('TO:','').strip('<>')); self.state='RCPT'; r="250 OK"
        elif verb=='DATA' and self.state=='RCPT': self.state='DATA'; r="354 Start mail"
        elif verb=='QUIT': self.state='DONE'; r="221 Bye"
        else: r=f"500 Unknown command {verb}"
        self.log.append((cmd,r)); return r
    def receive_data(self,data): self.data=data; self.state='READY'; return "250 OK"
if __name__=="__main__":
    msg=SMTPMessage("alice@test.com",["bob@test.com"],"Hello","Hi Bob!")
    assert "From: alice@test.com" in msg.to_mime()
    s=SMTPSession()
    assert s.command("EHLO client").startswith("250")
    assert s.command("MAIL FROM:<alice@test.com>")=="250 OK"
    assert s.command("RCPT TO:<bob@test.com>")=="250 OK"
    assert s.command("DATA").startswith("354")
    assert s.receive_data(msg.to_mime())=="250 OK"
    assert s.command("QUIT").startswith("221")
    print(f"SMTP session: {len(s.log)} commands")
    print("All tests passed!")

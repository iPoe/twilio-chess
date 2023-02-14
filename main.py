from twilio.rest import Client 
 
account_sid = 'AC49095a1abda910aed2b699341fb78739' 
auth_token = '3a654e59e332cf863bd2a93e5c659523' 
client = Client(account_sid, auth_token) 
 
message = client.messages.create( 
                              from_='whatsapp:+14155238886',  
                              body='Today we are gonna make a chess game',      
                              to='whatsapp:+573177947129' 
                          ) 
 
print(message.sid)

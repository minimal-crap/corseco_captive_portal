from twilio.rest import TwilioRestClient

account_sid = "AC26b85e7d1c4ecadc236f0b643206c382" # Your Account SID from www.twilio.com/console
auth_token  = "256b8d41342d516fc322864e17f22893"  # Your Auth Token from www.twilio.com/console

client = TwilioRestClient(account_sid, auth_token)

message = client.messages.create(body="Hello from Python",
    to="+919096311121",    # Replace with your phone number
    from_="+15005550006") # Replace with your Twilio number

print(message.sid)

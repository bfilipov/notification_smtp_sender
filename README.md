# App exposing endpoint for sending custom notifications through mail provider

## Abstract
The idea is to filter automated bots, that bypass captcha to send spam emails.
We have a simple method on frontend generating a token from some of the headers that are being send to backend. 
On the backend we are parsing the headers with the same algorithm and we are comparing the result to the provided token. 
It is comparably easy to reverse engineer, but that would require manual work, that I bet noone is willing to invest in. 
Will be confirmed empirically ;)

### run server
uvicorn smtp_sender.app:app --reload

### build & push docker
docker build -t email-sender .    
docker tag email-sender:latest bacebogo/email-sender:v1 (increment version!)   
docker push bacebogo/email-sender:v1   
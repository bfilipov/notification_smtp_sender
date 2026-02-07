# App exposing endpoint for sending custom notifications through mail provider


### run server
uvicorn smtp_sender.app:app --reload

### build & push docker
docker build -t email-sender .    
docker tag email-sender:latest bacebogo/email-sender:v1 (increment version!)   
docker push bacebogo/email-sender:v1   
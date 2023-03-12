Training Modello:
rasa train

Connessione a Telegram
1) Creare bot sul canale BotFather
2) Creare .env con le variabili
    ACCESS_TOKEN : (Token fornito dal botfather)
    VERIFY : (Nome scelto per il bot)
    WEBHOOK_URL : eseguire comando 'ngrok http 5005' su ngrok, inserire indirizzo restituito + /webhooks/telegram/webhook

Esecuzione
rasa run 
rasa run actions

import time
import requests

# 🔐 Infos Telegram
TELEGRAM_TOKEN = ""
TELEGRAM_IDS = [
    "",
    "",
]

# ✅ Références standards
PAIEMENTS_STANDARD = {"cb", "cash", "apple pay", "google pay"}
LIVRAISONS_STANDARD = {"clickandcollect", "ubereats", "deliveroo", "justeat"}

# 📬 Fonction d'envoi à plusieurs utilisateurs
def send_telegram_message(token, chat_ids, text):
    MAX_LEN = 4000
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    for chat_id in chat_ids:
        for i in range(0, len(text), MAX_LEN):
            chunk = text[i:i+MAX_LEN]
            payload = {'chat_id': chat_id, 'text': chunk}
            try:
                requests.post(url, data=payload)
            except Exception as e:
                print(f"Erreur lors de l'envoi à {chat_id} : {e}")

# 🔍 Analyse des restaurants O'Tacos
def analyze_otacos():
    url = "https://api.flyx.cloud/otacos/ordering/api/store/getanonymous/fr-FR"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_IDS, f"⚠️ Erreur fetch O'Tacos : {e}")
        return

    messages = []
    anomalies_found = False

    for resto in data.get("stores", []):
        name = resto.get("name", "Inconnu")
        payments = set([p.lower() for p in resto.get("payment_methods", [])])
        deliveries = set([d.lower() for d in resto.get("delivery_methods", [])])

        anomalies_paiement = [p for p in payments if p not in PAIEMENTS_STANDARD]
        anomalies_livraison = [d for d in deliveries if d not in LIVRAISONS_STANDARD]

        if anomalies_paiement or anomalies_livraison:
            anomalies_found = True
            msg = f"🏪 {name}\n"
            if anomalies_paiement:
                msg += f"  ❗️ Paiement(s) anormal(aux): {', '.join(anomalies_paiement)}\n"
            if anomalies_livraison:
                msg += f"  ❗️ Livraison(s) anormale(s): {', '.join(anomalies_livraison)}\n"
            messages.append(msg)

    if anomalies_found:
        send_telegram_message(
            TELEGRAM_TOKEN,
            TELEGRAM_IDS,
            "⚠️ Anomalies détectées dans les restaurants O’Tacos :\n\n" + "\n".join(messages)
        )
    else:
        send_telegram_message(
            TELEGRAM_TOKEN,
            TELEGRAM_IDS,
            "✅ Aucune anomalie détectée dans les restaurants O’Tacos."
        )

# 🔁 Exécution toutes les heures
if __name__ == "__main__":
    while True:
        analyze_otacos()
        time.sleep(3600)  # Pause 1h

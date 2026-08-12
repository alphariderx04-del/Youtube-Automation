# YouTube Upload Automation

Aap sirf `videos_to_upload` folder me video + thumbnail daalo — baaki (title,
description, tags, upload, schedule) sab automatic ho jaayega.

---

## Kya-kya karega ye system

1. `videos_to_upload` folder ko har 30 seconds me check karega
2. Naya video + matching thumbnail milte hi:
   - OpenAI GPT se title, description, tags generate karega
   - YouTube pe video upload karega (thumbnail set karke)
   - Aapke set kiye gaye time pe schedule/publish karega
3. Uploaded files ko `done` folder me move kar dega, log rakhega
4. Agar kuch fail ho jaaye to `failed` folder me daal dega aur log me error likhega

---

## Setup Steps (ek baar karna hai)

### 1. Google Cloud se YouTube API enable karo

1. https://console.cloud.google.com pe jao, naya project banao
2. "APIs & Services" > "Library" me "YouTube Data API v3" search karke enable karo
3. "APIs & Services" > "Credentials" > "Create Credentials" > "OAuth client ID"
   - Application type: **Desktop app**
4. JSON download karo, iska naam rakho `client_secrets.json`, project folder me daal do

### 2. OpenAI API key lo

1. https://platform.openai.com/api-keys se naya key banao
2. `.env.example` file ko `.env` naam se copy karo
3. `.env` me apni `OPENAI_API_KEY` daal do

### 3. Local machine pe ek baar authenticate karo

Server pe browser nahi hota, isliye pehli baar apne laptop pe ye karna padega:

```bash
pip install -r requirements.txt
python youtube_auth.py
```

Ye browser kholega, apne YouTube channel wale Google account se login karo.
Isse `token.pickle` file ban jaayegi.

### 4. Cloud server pe deploy karo

Kisi bhi VPS pe (DigitalOcean, AWS EC2 lightweight instance, Hetzner, etc.
$4-6/month wala bhi chalega):

```bash
# Poora project folder server pe upload karo (client_secrets.json aur
# token.pickle dono included hone chahiye)
scp -r youtube-automation root@your-server-ip:/root/

# Server pe login karke:
ssh root@your-server-ip
cd /root/youtube-automation

# Python aur dependencies install karo
apt update && apt install python3 python3-pip -y
pip3 install -r requirements.txt

# Test run karo pehle
python3 main.py
# Ctrl+C se rok do agar sab sahi chal raha hai

# 24x7 background me chalane ke liye systemd service setup karo
cp youtube-automation.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable youtube-automation
systemctl start youtube-automation

# Status check karne ke liye
systemctl status youtube-automation

# Logs dekhne ke liye
tail -f /root/youtube-automation/logs/automation.log
```

Bas ho gaya — ab server 24x7 folder watch karega, server restart hone pe bhi
automatically wapas chalu ho jaayega (Restart=always).

---

## Roz ka use (aapko sirf ye karna hai)

1. Video edit karo, thumbnail banao (Canva/Photoshop se)
2. Dono files ko same naam se rakho:
   - `episode5.mp4`
   - `episode5.jpg`
3. (Optional) `episode5.txt` me 1-2 line likh do video ke baare me — AI ko
   better title/description banane me madad milegi
4. In teeno files ko server ke `videos_to_upload` folder me daal do
   (SFTP/SCP/FileZilla se, ya server pe Google Drive sync bhi laga sakte ho)

Bas — agle 30 second ke andar video automatically process hokar YouTube pe
chala jaayega.

---

## .env settings samjho

| Setting | Kya karta hai |
|---|---|
| `DEFAULT_PRIVACY_STATUS` | `private` / `public` / `unlisted` |
| `SCHEDULE_DELAY_MINUTES` | 0 = turant publish, 60 = 1 ghante baad publish |
| `CHANNEL_NICHE` | AI ko batao aapka channel kis topic pe hai |
| `CHANNEL_TONE` | AI ko batao aapka style casual hai ya professional |

---

## Important notes

- **YouTube API daily quota**: Free tier me roughly 6 videos/din upload kar
  sakte ho (10,000 units/day quota, ek upload ~1600 units leta hai). Zyada
  chahiye to Google Cloud Console me quota increase request kar sakte ho.
- **Thumbnail** aap khud manually banaoge, bas naam video jaisa hi rakhna hai.
- Agar `token.pickle` expire ho jaaye (bahut mahino baad), to phir se
  `python youtube_auth.py` chalana padega apne laptop pe.

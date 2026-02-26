# SOC Platform — Guide Manuel Complet

---

## Table des matières

1. [Prérequis](#1-prérequis)
2. [Installation](#2-installation)
3. [Configuration](#3-configuration)
4. [Démarrage de la plateforme](#4-démarrage-de-la-plateforme)
5. [Interface Web — Navigation](#5-interface-web--navigation)
6. [Dashboard SOC](#6-dashboard-soc)
7. [Log Viewer](#7-log-viewer)
8. [IDS / IPS Console](#8-ids--ips-console)
9. [Network Map](#9-network-map)
10. [Security Alerts](#10-security-alerts)
11. [Settings — Notifications](#11-settings--notifications)
12. [Collecte de logs avec Filebeat](#12-collecte-de-logs-avec-filebeat)
13. [API REST](#13-api-rest)
14. [Architecture des données](#14-architecture-des-données)
15. [Maintenance et opérations](#15-maintenance-et-opérations)
16. [Dépannage](#16-dépannage)
17. [Sécurité en production](#17-sécurité-en-production)

---

## 1. Prérequis

### Système hôte

| Composant | Minimum | Recommandé |
|---|---|---|
| OS | Ubuntu 20.04 / Debian 11 | Ubuntu 22.04 LTS |
| CPU | 4 cœurs | 8 cœurs |
| RAM | 8 Go | 16 Go |
| Disque | 50 Go SSD | 200 Go SSD |
| Réseau | 100 Mbps | 1 Gbps |

### Logiciels requis

```bash
# Docker Engine (>= 24.x)
curl -fsSL https://get.docker.com | bash
sudo usermod -aG docker $USER

# Docker Compose (>= 2.x) — inclus avec Docker Desktop
docker compose version

# Git
sudo apt install -y git

# Optionnel : nmap (pour scans hors Docker)
sudo apt install -y nmap
```

### Ports utilisés

| Port | Service | Direction |
|---|---|---|
| 80 | Nginx (HTTP) | Entrant |
| 443 | Nginx (HTTPS) | Entrant |
| 5044 | Logstash Beats (Linux/Windows) | Entrant |
| 5045 | Logstash Beats (Windows Events) | Entrant |
| 5140 | Logstash Syslog (Firewall) | Entrant |
| 5145 | Logstash Syslog (Network) | Entrant |

---

## 2. Installation

### Cloner / Copier le projet

```bash
# Copier le dossier soc-platform sur votre serveur Linux
scp -r soc-platform/ user@your-server:/opt/soc-platform

# Ou sur le serveur directement
sudo mkdir -p /opt/soc-platform
sudo chown $USER:$USER /opt/soc-platform
cp -r ~/soc-platform/* /opt/soc-platform/
cd /opt/soc-platform
```

### Ajuster les permissions

```bash
chmod +x scripts/deploy.sh
chmod 600 .env
```

---

## 3. Configuration

### 3.1 Fichier .env

```bash
cp .env.example .env
nano .env
```

Remplir toutes les valeurs :

```env
# Base de données PostgreSQL
POSTGRES_DB=socdb
POSTGRES_USER=socuser
POSTGRES_PASSWORD=MotDePasse_Fort_Ici

# Redis
REDIS_PASSWORD=Redis_MotDePasse_Fort

# Clé secrète JWT (minimum 32 caractères, aléatoire)
SECRET_KEY=generez-une-cle-aleatoire-de-64-chars-ici

# Telegram (optionnel — pour les alertes)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=-100123456789

# WhatsApp via Twilio (optionnel)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
WHATSAPP_TO=whatsapp:+33612345678
```

### 3.2 Créer un bot Telegram

1. Ouvrir Telegram → chercher `@BotFather`
2. Envoyer `/newbot` → suivre les instructions
3. Copier le token dans `TELEGRAM_BOT_TOKEN`
4. Ajouter le bot à un groupe ou canal
5. Récupérer le Chat ID :
   ```bash
   curl "https://api.telegram.org/bot<VOTRE_TOKEN>/getUpdates"
   # Le champ "chat.id" est votre TELEGRAM_CHAT_ID
   ```

### 3.3 Configurer le réseau Suricata

Éditer `suricata/suricata.yaml` pour adapter le réseau interne :

```yaml
vars:
  address-groups:
    HOME_NET: "[192.168.0.0/16,10.0.0.0/8,172.16.0.0/12]"
    # Adapter selon votre réseau d'entreprise
```

Changer l'interface réseau surveillée :

```yaml
af-packet:
  - interface: eth0   # Remplacer par votre interface (ip a)
```

---

## 4. Démarrage de la plateforme

### Démarrage complet

```bash
cd /opt/soc-platform

# Première installation
bash scripts/deploy.sh

# Démarrages suivants
docker compose up -d

# Vérifier l'état
docker compose ps
```

### Vérifier que tout fonctionne

```bash
# Santé des services
docker compose ps

# Logs en temps réel
docker compose logs -f backend

# Test API
curl http://localhost/api/v1/health
# Réponse attendue : {"status":"ok","service":"SOC Platform"}
```

### Accès à l'interface

| URL | Description |
|---|---|
| `http://votre-ip` | Interface SOC principale |
| `http://votre-ip/api/v1/docs` | Documentation API Swagger |
| `http://votre-ip/api/v1/health` | Health check |

### Identifiants par défaut

```
Username : admin
Password : admin
```

> Changer le mot de passe admin immédiatement en production :
> ```bash
> docker compose exec postgres psql -U socuser -d socdb \
>   -c "UPDATE users SET password_hash='\$2b\$12\$NOUVEAU_HASH' WHERE username='admin';"
> ```

---

## 5. Interface Web — Navigation

### Structure de la barre latérale

```
[S] SOC Platform
├── Dashboard    — Vue d'ensemble en temps réel
├── Logs         — Recherche et analyse des logs
├── IDS/IPS      — Console de détection d'intrusion
├── Network      — Cartographie réseau et scans
├── Alerts       — Gestion des alertes de sécurité
└── Settings     — Configuration des notifications
```

### Barre du haut

- **Titre de page** — Page active
- **Horloge UTC** — Heure système en temps réel
- **Indicateur LIVE/OFFLINE** — Statut de la connexion WebSocket
- **Profil utilisateur** — Nom et rôle (admin / analyst / viewer)

---

## 6. Dashboard SOC

Le dashboard est la page principale du SOC. Il se rafraîchit automatiquement via WebSocket.

### KPIs (6 indicateurs)

| Indicateur | Description |
|---|---|
| **Alerts Today** | Nombre total d'alertes sur les dernières 24h |
| **Critical** | Alertes de criticité CRITICAL |
| **Open** | Alertes avec statut "open" (non traitées) |
| **IDS Alerts** | Alertes générées par Suricata |
| **Assets** | Machines actives sur le réseau |
| **Logs Today** | Volume de logs indexés aujourd'hui |

### Graphiques

**Alert Timeline (24h)**
- Histogramme des alertes heure par heure
- Permet d'identifier les pics d'activité
- Axe X : heure (UTC), axe Y : nombre d'alertes

**Top Source IPs**
- Barres horizontales des IPs générant le plus d'alertes
- Utile pour identifier des sources d'attaque

**Top Threats**
- Liste des types de menaces les plus fréquents
- Avec niveau de sévérité associé

**Live Feed**
- Flux d'activité en temps réel
- Points colorés selon la sévérité (rouge = critical, orange = high, jaune = medium, cyan = low)

---

## 7. Log Viewer

### Filtres de recherche

| Filtre | Type | Exemple |
|---|---|---|
| **Search** | Texte libre | `failed password`, `connection refused` |
| **Severity** | Liste | `critical`, `high`, `medium`, `low`, `info` |
| **Type** | Liste | `system`, `network`, `application`, `firewall` |
| **Source IP** | IP | `192.168.1.45` |
| **Dest IP** | IP | `10.0.0.1` |
| **Protocol** | Liste | `TCP`, `UDP`, `ICMP` |
| **Service** | Texte | `ssh`, `http`, `ftp` |

### Utilisation

1. Remplir un ou plusieurs filtres
2. Cliquer sur **SEARCH**
3. Cliquer sur une ligne pour voir le **détail complet**
4. Naviguer avec les boutons `<` `>` pour la pagination
5. Cliquer **RESET** pour effacer les filtres

### Cas d'usage typiques

```
# Rechercher toutes les tentatives SSH échouées
Search: "failed password"
Type: system

# Logs d'un firewall pour une IP suspecte
Source IP: 185.220.101.45
Type: firewall

# Activité HTTP suspecte
Service: http
Severity: high

# Logs d'hier sur un host précis
# (utiliser date_from / date_to via l'API)
```

### Lecture d'une entrée de log

```
Timestamp  | Severity | Host        | Source IP    | Type    | Program | Message
-----------+----------+-------------+--------------+---------+---------+--------
2026-02-25 | high     | prod-web-01 | 185.220.1.45 | system  | sshd    | Failed password for root...
14:32:01   |          |             |              |         |         |
```

---

## 8. IDS / IPS Console

### Modes de fonctionnement

| Mode | Description | Action |
|---|---|---|
| **IDS** | Détection uniquement | Génère des alertes, ne bloque pas |
| **IPS** | Prévention active | Bloque le trafic suspect via NFQUEUE |
| **OFF** | Désactivé | Suricata arrêté |

### Changer de mode

1. Cliquer sur le bouton **IDS**, **IPS**, ou **OFF**
2. Le changement est immédiat en base de données
3. Pour activer IPS en production, Suricata doit être configuré avec NFQUEUE :
   ```bash
   # Sur le serveur hôte
   iptables -I FORWARD -j NFQUEUE --queue-num 0
   iptables -I INPUT -j NFQUEUE --queue-num 0
   ```

### Lecture des alertes IDS

| Colonne | Description |
|---|---|
| **Timestamp** | Heure de détection |
| **Severity** | critical / high / medium / low |
| **Category** | network-scan, attempted-admin, dos-attack... |
| **Source** | IP:Port source de l'attaque |
| **Destination** | IP:Port ciblé |
| **Protocol** | TCP / UDP / ICMP |
| **Action** | `alert` (IDS) ou `drop` (IPS) |
| **Rule** | Identifiant de la règle Suricata (SID) |
| **Message** | Description de la détection |

### Types d'attaques détectés

```
port_scan      — Scan de ports (Nmap, masscan...)
brute_force    — Attaque par force brute SSH, FTP, HTTP
dos            — Déni de service (SYN flood, ICMP flood)
web_attack     — Injection SQL, attaques HTTP
anomaly        — Comportement réseau anormal
malware        — Communication C2, signatures malware
```

### Ajouter une règle Suricata personnalisée

Via l'API (voir section 13) ou directement dans le fichier :

```bash
nano /opt/soc-platform/suricata/rules/local.rules
```

Exemple de règle :

```
# Bloquer un scan vers le port 3306 (MySQL)
alert tcp any any -> $HOME_NET 3306 (
  msg:"SOC MYSQL SCAN DETECTED";
  flags:S;
  threshold:type both,track by_src,count 5,seconds 10;
  classtype:network-scan;
  sid:9000020;
  rev:1;
)
```

Recharger les règles :

```bash
docker compose exec suricata suricatasc -c reload-rules
```

---

## 9. Network Map

### Lancer un scan réseau

1. Entrer la **cible** dans le champ Target :
   - Plage CIDR : `192.168.1.0/24`
   - Host unique : `10.0.0.15`
   - Plage d'IPs : `10.0.0.1-50`

2. Choisir le **type de scan** :

| Type | Commande Nmap | Durée | Usage |
|---|---|---|---|
| **Quick** | `-sn` | ~10s | Détection de machines actives (ping sweep) |
| **Standard** | `-sS -sV -O --top-ports 1000` | ~2min | Ports courants + services + OS |
| **Full** | `-sS -sV -O -p-` | ~20min | Tous les 65535 ports |
| **Vuln** | `-sV --script vuln` | ~30min | Détection de vulnérabilités |

3. Cliquer **SCAN** — le scan s'exécute en arrière-plan
4. Cliquer **Refresh** pour voir les nouveaux assets

### Tableau des assets

| Colonne | Description |
|---|---|
| Point vert/rouge | Machine active / inactive |
| **IP Address** | Adresse IP de la machine |
| **Hostname** | Nom DNS résolu |
| **OS** | Système d'exploitation détecté |
| **Type** | server / workstation / network / iot |
| **Criticality** | low / medium / high / critical |
| **Last Seen** | Dernière détection |
| **Open Ports** | Nombre de ports ouverts |

### Détail d'un asset

Cliquer sur une ligne pour afficher :
- Informations complètes (IP, hostname, OS, type)
- **Tous les ports** avec état (open / closed / filtered), protocole et service

### Network Changes

Panneau en bas à droite listant les **changements détectés** :
- `new_host` — Nouvelle machine apparue sur le réseau
- `port_opened` — Nouveau port ouvert sur un asset connu
- `port_closed` — Port précédemment ouvert maintenant fermé
- `service_changed` — Service sur un port a changé

Cliquer l'icône de coche pour **acquitter** un changement.

---

## 10. Security Alerts

### Filtres

- **Severity** : `critical`, `high`, `medium`, `low`, `info`
- **Status** : `open`, `investigating`, `resolved`, `false_positive`

### Workflow de traitement d'une alerte

```
OPEN
  │
  ▼
INVESTIGATING  ← Un analyste prend en charge l'alerte
  │
  ├─► RESOLVED         ← Incident confirmé et résolu
  └─► FALSE_POSITIVE   ← Fausse détection
```

1. Cliquer sur une alerte pour voir le **détail**
2. Dans le panneau de droite, cliquer sur :
   - **Investigating** — Prendre en charge
   - **Resolved** — Marquer comme résolu
   - **False positive** — Marquer comme fausse détection

### Colonnes du tableau

| Colonne | Description |
|---|---|
| **Time** | Horodatage de création |
| **Severity** | Niveau de criticité |
| **Type** | Type d'alerte (brute_force, port_scan...) |
| **Title** | Titre descriptif |
| **Source** | IP source de l'attaque |
| **Dest** | IP destination ciblée |
| **Status** | État de traitement |

### Niveaux de sévérité

| Niveau | Couleur | Description | Délai de réponse |
|---|---|---|---|
| **CRITICAL** | Rouge vif | Compromission probable, action immédiate | < 15 min |
| **HIGH** | Orange | Attaque active confirmée | < 1 heure |
| **MEDIUM** | Jaune | Activité suspecte | < 4 heures |
| **LOW** | Cyan | Événement à surveiller | < 24 heures |
| **INFO** | Gris | Informatif | Aucun |

---

## 11. Settings — Notifications

### Configurer Telegram

1. Aller dans **Settings**
2. Renseigner :
   - **Bot Token** : token fourni par @BotFather
   - **Chat ID** : ID de votre groupe/canal Telegram
3. Cliquer **Test** pour envoyer un message de test
4. Cliquer **Save**

### Configurer WhatsApp (Twilio)

1. Créer un compte sur [twilio.com](https://www.twilio.com)
2. Activer le sandbox WhatsApp dans la console Twilio
3. Renseigner dans Settings :
   - **Account SID** : depuis la console Twilio
   - **Auth Token** : depuis la console Twilio
   - **From** : `whatsapp:+14155238886` (numéro sandbox Twilio)
   - **To** : `whatsapp:+33612345678` (votre numéro)
4. Cliquer **Test**

### Format des alertes reçues

**Telegram :**
```
🔴 [CRITICAL] SSH Brute Force

⏱ 2026-02-25 14:32:00 UTC
📋 Type     : brute_force
🌐 Source   : 185.220.101.45:54321
🎯 Cible    : 10.0.1.15:22
📡 Service  : SSH
⚡ Protocole: TCP
🔑 Règle    : 9000002
```

**WhatsApp :**
```
[CRITICAL] SSH Brute Force
Type: brute_force
Source: 185.220.101.45:54321
Target: 10.0.1.15:22
Service: SSH
Protocol: TCP
Time: 2026-02-25 14:32:00
```

### Seuil d'alerte

Par défaut, les notifications sont envoyées pour les sévérités **CRITICAL** et **HIGH** uniquement.
Pour modifier : éditer `backend/modules/alerts/router.py`, ligne :
```python
if alert.severity in ["critical", "high"]:
```

---

## 12. Collecte de logs avec Filebeat

### Installation de Filebeat sur un serveur Linux

```bash
# Sur le serveur à monitorer
curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-8.11.0-linux-x86_64.tar.gz
tar xzvf filebeat-8.11.0-linux-x86_64.tar.gz
cd filebeat-8.11.0-linux-x86_64/
```

### Configuration Filebeat

```yaml
# filebeat.yml

filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/syslog
      - /var/log/auth.log
    fields:
      type: syslog
    fields_under_root: true

  - type: log
    enabled: true
    paths:
      - /var/log/nginx/access.log
    fields:
      type: application
      service: nginx
    fields_under_root: true

output.logstash:
  hosts: ["IP_DU_SOC:5044"]
```

```bash
./filebeat -e -c filebeat.yml
```

### Pour Windows (Winlogbeat)

```yaml
# winlogbeat.yml
winlogbeat.event_logs:
  - name: Security
    event_id: 4625, 4648, 4720, 4728, 4732
  - name: System
  - name: Application

output.logstash:
  hosts: ["IP_DU_SOC:5045"]
```

### Pour les firewalls (syslog)

Configurer votre firewall pour envoyer les logs syslog vers :
```
IP_DU_SOC:5140 (UDP ou TCP)
```

Formats supportés : Cisco ASA, pfSense, iptables, Fortinet.

---

## 13. API REST

### Authentification

```bash
# Obtenir un token
curl -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Utiliser le token
TOKEN="votre_access_token"
curl -H "Authorization: Bearer $TOKEN" http://localhost/api/v1/dashboard/summary
```

### Endpoints principaux

#### Dashboard
```bash
GET /api/v1/dashboard/summary      # KPIs SOC
GET /api/v1/dashboard/timeline     # Timeline 24h
GET /api/v1/dashboard/top-threats  # Top menaces
GET /api/v1/dashboard/top-sources  # Top IPs sources
```

#### Logs
```bash
# Recherche avancée
POST /api/v1/logs/search
{
  "query": "failed password",
  "severity": "high",
  "src_ip": "192.168.1.45",
  "page": 1,
  "page_size": 50
}

GET /api/v1/logs/stats              # Statistiques
```

#### IDS/IPS
```bash
GET  /api/v1/ids/status             # Statut + stats
GET  /api/v1/ids/alerts?limit=100   # Alertes Suricata
PUT  /api/v1/ids/mode               # Changer mode
{"mode": "ips"}

GET  /api/v1/ids/rules              # Règles actives
POST /api/v1/ids/rules              # Ajouter une règle
{
  "name": "MySQL Scan",
  "content": "alert tcp any any -> $HOME_NET 3306 ...",
  "severity": "medium"
}
```

#### Network
```bash
GET  /api/v1/network/assets         # Inventaire
POST /api/v1/network/scan           # Lancer scan
{"target": "192.168.1.0/24", "scan_type": "standard"}

GET  /api/v1/network/scan/{id}      # Résultats scan
GET  /api/v1/network/changes        # Changements réseau
PUT  /api/v1/network/changes/{id}/ack  # Acquitter
```

#### Alertes
```bash
GET  /api/v1/alerts?severity=critical&status=open
POST /api/v1/alerts                 # Créer une alerte
PUT  /api/v1/alerts/{id}/status
{"status": "investigating"}
```

### Documentation interactive

Accéder à `http://votre-ip/api/v1/docs` pour l'interface Swagger complète avec la possibilité de tester tous les endpoints directement depuis le navigateur.

---

## 14. Architecture des données

### Flux de données

```
Sources                Pipeline                Stockage
------                 --------                --------
Linux syslog    ─────► Logstash ──────────────► Elasticsearch (logs)
Windows Events  ─────► Logstash ──────────────► Elasticsearch (logs)
Firewall syslog ─────► Logstash ──────────────► Elasticsearch (logs)
                              └────────────────► Kafka (stream)
                                                     │
Network traffic ─────► Suricata ─────────────────────┘
                                                     │
                                                     ▼
                                              Backend FastAPI
                                                     │
                                        ┌────────────┴────────────┐
                                        ▼                         ▼
                                   PostgreSQL                  Redis
                                (alertes, assets,          (cache, sessions,
                                 scans, config)              WebSocket pub/sub)
```

### Rétention des données

| Stockage | Données | Rétention par défaut |
|---|---|---|
| Elasticsearch | Logs bruts | 7 jours (configurable) |
| PostgreSQL | Alertes, assets, scans | Illimitée |
| Kafka | Events stream | 7 jours |
| Redis | Cache/sessions | 24h (sessions) |

### Modifier la rétention Elasticsearch

```bash
# Supprimer les index de plus de 30 jours
curl -X DELETE "http://localhost:9200/soc-logs-$(date -d '30 days ago' +%Y.%m.%d)"

# Politique ILM automatique
curl -X PUT "http://localhost:9200/_ilm/policy/soc-logs-policy" \
  -H "Content-Type: application/json" \
  -d '{
    "policy": {
      "phases": {
        "delete": {
          "min_age": "30d",
          "actions": { "delete": {} }
        }
      }
    }
  }'
```

---

## 15. Maintenance et opérations

### Commandes courantes

```bash
# Statut de tous les services
docker compose ps

# Logs d'un service spécifique
docker compose logs -f backend
docker compose logs -f worker
docker compose logs -f elasticsearch

# Redémarrer un service
docker compose restart backend

# Arrêter la plateforme
docker compose down

# Arrêter sans supprimer les données
docker compose stop

# Mise à jour du code
docker compose down
git pull  # ou copier les nouveaux fichiers
docker compose build --no-cache backend frontend
docker compose up -d
```

### Backup des données

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backup/soc

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker compose exec -T postgres pg_dump -U socuser socdb \
  | gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

# Backup Elasticsearch (snapshot)
curl -X PUT "http://localhost:9200/_snapshot/backup_$DATE" \
  -H "Content-Type: application/json" \
  -d '{"indices": "soc-logs-*", "ignore_unavailable": true}'

echo "Backup completed: $BACKUP_DIR"
```

### Restauration PostgreSQL

```bash
gunzip -c /backup/soc/postgres_20260225_143200.sql.gz \
  | docker compose exec -T postgres psql -U socuser socdb
```

### Surveillance de la plateforme

```bash
# Utilisation mémoire des containers
docker stats --no-stream

# Espace disque Elasticsearch
curl http://localhost:9200/_cat/indices?v

# File Kafka
docker compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe --all-groups
```

### Rotation des logs applicatifs

```bash
# Configurer logrotate pour les logs Docker
cat > /etc/logrotate.d/docker-containers << EOF
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    missingok
    delaycompress
    copytruncate
}
EOF
```

---

## 16. Dépannage

### Le backend ne démarre pas

```bash
docker compose logs backend
```

Causes fréquentes :
- PostgreSQL pas encore prêt → attendre 30s puis `docker compose restart backend`
- Erreur de variable d'environnement → vérifier `.env`
- Port 8000 déjà utilisé → `sudo lsof -i :8000`

### Elasticsearch échoue à démarrer

```bash
# Erreur max virtual memory
sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### Kafka ne reçoit pas de messages

```bash
# Vérifier que les topics existent
docker compose exec kafka kafka-topics \
  --bootstrap-server localhost:9092 --list

# Créer le topic manuellement si absent
docker compose exec kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create --topic soc-logs --partitions 3 --replication-factor 1
```

### Interface blanche / erreur 502

```bash
# Vérifier que frontend et backend tournent
docker compose ps

# Vérifier Nginx
docker compose logs nginx

# Tester le backend directement
curl http://localhost:8000/api/v1/health
```

### Alertes Telegram non reçues

1. Vérifier le token : `curl "https://api.telegram.org/bot<TOKEN>/getMe"`
2. Vérifier que le bot est dans le groupe/canal
3. Vérifier les logs du worker : `docker compose logs worker`
4. Tester manuellement via l'API :
   ```bash
   curl -X POST http://localhost/api/v1/notifications/test \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"provider":"telegram"}'
   ```

### Suricata ne détecte rien

```bash
# Vérifier que Suricata tourne
docker compose exec suricata suricata --build-info

# Vérifier les logs Suricata
docker compose exec suricata tail -f /var/log/suricata/suricata.log

# Vérifier que l'interface est correcte
docker compose exec suricata ip a
```

### Les scans réseau échouent

```bash
# Vérifier que nmap est installé dans le container
docker compose exec backend nmap --version

# Test scan manuel
docker compose exec backend nmap -sn 192.168.1.1
```

---

## 17. Sécurité en production

### Checklist obligatoire avant mise en production

- [ ] Changer le mot de passe `admin` par défaut
- [ ] Générer un `SECRET_KEY` aléatoire de 64+ caractères
- [ ] Changer tous les mots de passe dans `.env`
- [ ] Activer HTTPS (certificat SSL)
- [ ] Restreindre l'accès à l'interface (VPN ou IP whitelist)
- [ ] Activer le firewall système (`ufw`)
- [ ] Désactiver l'accès direct aux ports internes (5432, 9200, 6379...)

### Activer HTTPS avec Let's Encrypt

```bash
# Installer certbot
sudo apt install -y certbot

# Obtenir un certificat
sudo certbot certonly --standalone -d votre-domaine.com

# Copier les certificats
sudo cp /etc/letsencrypt/live/votre-domaine.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/votre-domaine.com/privkey.pem nginx/ssl/key.pem
```

Décommenter le bloc HTTPS dans `nginx/nginx.conf` :
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ...
}
```

### Pare-feu système (ufw)

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5044/tcp   # Filebeat (si agents externes)
sudo ufw allow 5140/udp   # Syslog firewall (si besoin)
sudo ufw enable
```

### Gestion des utilisateurs SOC

Créer un analyste (rôle limité) :

```bash
# Générer un hash bcrypt
docker compose exec backend python3 -c \
  "from passlib.context import CryptContext; \
   ctx = CryptContext(schemes=['bcrypt']); \
   print(ctx.hash('motdepasse_analyste'))"

# Insérer en base
docker compose exec postgres psql -U socuser -d socdb -c \
  "INSERT INTO users (username, email, password_hash, role) \
   VALUES ('analyste1', 'analyste1@soc.local', 'HASH_ICI', 'analyst');"
```

Rôles disponibles :

| Rôle | Permissions |
|---|---|
| `admin` | Accès complet, gestion utilisateurs, configuration |
| `analyst` | Lecture + traitement des alertes, pas de configuration |
| `viewer` | Lecture seule |

---

## Annexe — Variables d'environnement complètes

| Variable | Description | Requis |
|---|---|---|
| `POSTGRES_DB` | Nom de la base de données | Oui |
| `POSTGRES_USER` | Utilisateur PostgreSQL | Oui |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL | Oui |
| `REDIS_PASSWORD` | Mot de passe Redis | Oui |
| `SECRET_KEY` | Clé secrète JWT (min 32 chars) | Oui |
| `TELEGRAM_BOT_TOKEN` | Token du bot Telegram | Non |
| `TELEGRAM_CHAT_ID` | ID du chat/groupe Telegram | Non |
| `TWILIO_ACCOUNT_SID` | SID du compte Twilio | Non |
| `TWILIO_AUTH_TOKEN` | Token d'auth Twilio | Non |
| `TWILIO_WHATSAPP_FROM` | Numéro WhatsApp expéditeur | Non |
| `WHATSAPP_TO` | Numéro WhatsApp destinataire | Non |

---

*SOC Platform v1.0 — Document interne confidentiel*

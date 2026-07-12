# Meyer RAG — Chatbot AMHE autour de Joachim Meyer

## 1. Présentation du projet

Ce projet est une application de chatbot RAG consacrée à l’étude de l’épée longue chez Joachim Meyer.

L’objectif est de transformer un prototype simple de chatbot en une application plus robuste, structurée et exploitable. Le chatbot permet à un utilisateur de poser des questions sur un corpus documentaire, d’obtenir des réponses générées par un LLM et de consulter les sources utilisées pour produire la réponse.

Le projet s’appuie sur une architecture RAG, c’est-à-dire une génération augmentée par récupération documentaire :

1. chargement du corpus ;
2. découpage des documents en morceaux exploitables ;
3. génération d’embeddings ;
4. stockage des documents, chunks et embeddings en base ;
5. recherche vectorielle des passages pertinents ;
6. construction d’un prompt enrichi avec les sources retrouvées ;
7. appel à un modèle LLM via Groq ;
8. affichage de la réponse dans une interface Streamlit ;
9. sauvegarde des conversations et des sources utilisées.

Le thème choisi est volontairement spécialisé : l’épée longue dans les traités de Joachim Meyer. Ce choix permet de tester le RAG sur un corpus réel, multilingue, technique et historiquement complexe.

---

## 2. Objectifs du projet

Le projet répond à plusieurs objectifs :

- améliorer un chatbot initialement simple ;
- rendre l’application plus structurée ;
- gérer une vraie base documentaire ;
- permettre une conversation avec historique ;
- rendre les réponses plus contrôlables grâce aux paramètres de génération ;
- afficher les sources utilisées ;
- ajouter une première gestion des erreurs ;
- préparer un déploiement possible ;
- documenter clairement l’architecture, les choix techniques, les limites et les pistes d’amélioration.

Ce projet correspond à une amélioration progressive du prototype réalisé en cours.

---

## 3. Fonctionnalités principales

La version actuelle permet :

- de poser des questions sur le corpus Meyer ;
- de choisir un mode de réponse ;
- de choisir un niveau de détail ;
- de récupérer des passages pertinents grâce à une recherche vectorielle ;
- de générer une réponse avec un modèle Groq ;
- d’afficher les sources utilisées ;
- de sauvegarder les conversations en base de données ;
- de charger une ancienne conversation depuis l’interface ;
- de lancer le projet en local ;
- de lancer le projet avec Docker Compose ;
- de préparer un déploiement futur.

---

## 4. Corpus utilisé

Le corpus est centré sur Joachim Meyer et l’épée longue.

Les sources principales sont des fichiers Markdown issus de Wiktenauer :

- transcription allemande du traité imprimé de 1570 ;
- traduction anglaise du traité de 1570 ;
- transcription allemande du manuscrit de Munich / Veldenz de 1561 ;
- traduction anglaise du manuscrit de Munich / Veldenz ;
- transcription allemande du manuscrit Solms / Lund de 1563 ;
- traduction anglaise du manuscrit Solms / Lund.

Des PDF français sont également utilisés comme sources secondaires :

- traduction française de l’épée longue de Meyer ;
- version Munich ;
- version Mégamix.

Les transcriptions allemandes sont considérées comme les sources les plus importantes. Les traductions anglaises et françaises servent d’aide à la compréhension, mais elles ne remplacent pas les sources primaires.

---

## 5. Structure du projet

```txt
app-meyer/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat_routes.py
│   │   │   ├── conversation_routes.py
│   │   │   └── document_routes.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   │
│   │   ├── models/
│   │   │   ├── chunk.py
│   │   │   ├── conversation.py
│   │   │   ├── document.py
│   │   │   └── message.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── chat.py
│   │   │   └── source.py
│   │   │
│   │   ├── scripts/
│   │   │   └── ingest_corpus.py
│   │   │
│   │   ├── services/
│   │   │   ├── chunking_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── groq_service.py
│   │   │   ├── loader_service.py
│   │   │   ├── prompt_service.py
│   │   │   ├── rag_service.py
│   │   │   └── retrieval_service.py
│   │   │
│   │   └── main.py
│   │
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── streamlit_app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── data/
│   ├── 1561-munich/
│   ├── 1563-solms/
│   ├── 1570/
│   └── secondary/
│
├── scripts/
│   ├── start_app.sh
│   ├── stop_app.sh
│   └── reset_app.sh
│
├── docker-compose.yml
├── Makefile
├── .gitignore
└── README.md
```

---

## 6. Description de l’architecture

### 6.1 Backend FastAPI

Le backend est responsable de toute la logique RAG.

Il gère :

- le chargement du corpus ;
- le découpage des documents ;
- la génération des embeddings ;
- le stockage dans PostgreSQL ;
- la recherche vectorielle avec pgvector ;
- la construction du prompt ;
- l’appel au modèle Groq ;
- la sauvegarde des conversations ;
- l’exposition des routes API.

Routes principales :

```txt
GET  /health
GET  /documents
GET  /documents/stats
GET  /conversations
GET  /conversations/{conversation_id}
POST /chat
```

### 6.2 Frontend Streamlit

Le frontend est l’interface utilisateur.

Il permet :

- de poser une question ;
- de choisir le mode de réponse ;
- de choisir le niveau de détail ;
- de consulter les sources ;
- de créer une nouvelle conversation ;
- de charger une ancienne conversation ;
- d’afficher les messages sous forme de chat.

### 6.3 Base PostgreSQL + pgvector

La base de données stocke :

- les documents ;
- les chunks ;
- les embeddings ;
- les conversations ;
- les messages ;
- les sources associées aux réponses.

L’extension `pgvector` permet de faire une recherche de similarité directement dans PostgreSQL.

---

## 7. Choix techniques

### 7.1 FastAPI

FastAPI a été choisi pour le backend car il permet de créer rapidement une API claire, robuste et automatiquement documentée.

La documentation Swagger est disponible à l’adresse :

```txt
http://localhost:8000/docs
```

### 7.2 Streamlit

Streamlit a été choisi pour l’interface utilisateur car il permet de créer rapidement une interface de démonstration exploitable sans développer un frontend complet en React ou Vue.

Ce choix est adapté au contexte du TP, car l’objectif est de produire une application IA fonctionnelle et démontrable.

### 7.3 PostgreSQL + pgvector

PostgreSQL permet de stocker les données applicatives classiques :

- conversations ;
- messages ;
- documents ;
- métadonnées.

L’extension `pgvector` permet de stocker les embeddings et de réaliser la recherche vectorielle.

Ce choix est plus robuste qu’un simple stockage en fichiers `.npy` ou `.json`.

### 7.4 Embeddings

Le modèle d’embedding utilisé est :

```txt
intfloat/multilingual-e5-base
```

Ce modèle a été choisi car le corpus est multilingue :

- allemand ;
- anglais ;
- français.

Les textes sont encodés avec les préfixes recommandés pour les modèles E5 :

```txt
query: ...
passage: ...
```

Le préfixe `query:` est utilisé pour les questions utilisateur.  
Le préfixe `passage:` est utilisé pour les chunks documentaires.

### 7.5 Modèle de génération

Le modèle utilisé via Groq est :

```txt
llama-3.1-8b-instant
```

Il est utilisé pour générer une réponse à partir du contexte récupéré par le RAG.

Le choix de Groq permet d’obtenir des réponses rapides avec un modèle accessible par API.

---

## 8. Gestion de la température

La température contrôle le degré de créativité du modèle.

Dans le projet, la température est utilisée comme paramètre technique de génération.

Valeurs à tester :

```txt
0     → réponse plus déterministe
0.5   → équilibre entre précision et reformulation
1     → réponse plus créative, mais plus risquée
```

Analyse attendue :

| Température | Comportement attendu | Avantages | Risques |
|---|---|---|---|
| 0 | Réponse stable et déterministe | Plus cohérent pour une réponse documentaire | Moins naturel |
| 0.5 | Réponse équilibrée | Bon compromis pour explication pédagogique | Peut reformuler davantage |
| 1 | Réponse plus créative | Utile pour générer des drills ou idées de séance | Risque plus élevé d’imprécision |

Pour un usage documentaire, une température basse est préférable.  
Pour un mode pédagogique ou créatif, une température moyenne peut être plus adaptée.

Dans la version actuelle, la température par défaut est fixée à :

```txt
0.2
```

Ce choix vise à limiter les hallucinations tout en gardant une réponse lisible.

Évolution prévue : permettre le choix dynamique de la température depuis l’interface Streamlit.

---

## 9. Modes de réponse

L’application propose plusieurs modes.

### 9.1 Question générale / synthèse

Ce mode sert aux questions larges sur le contexte, les principes ou l’interprétation générale.

Exemple :

```txt
Meyer propose-t-il une escrime de jeu ou une escrime pour la vie ?
```

### 9.2 Recherche documentaire

Ce mode sert à retrouver et synthétiser les passages du corpus.

Exemple :

```txt
Que dit Meyer sur le Vor et le Nach ?
```

### 9.3 Explication technique

Ce mode sert à expliquer une notion pour un pratiquant.

Exemple :

```txt
Explique-moi le Zwerchhau pour un débutant.
```

### 9.4 Création de drill

Ce mode sert à créer un exercice d’entraînement.

Exemple :

```txt
Crée un drill de 10 minutes sur le Krumphau.
```

### 9.5 Fiche pédagogique

Ce mode sert à produire un support pour instructeur.

Exemple :

```txt
Fais-moi une fiche pédagogique sur le travail du Fort et du Faible.
```

---

## 10. Niveau de détail des réponses

L’interface permet de choisir la verbosité de la réponse :

```txt
Court
Normal
Détaillé
Cours complet
```

Cette option permet d’adapter la réponse au besoin utilisateur.

Exemples :

- réponse courte pour une vérification rapide ;
- réponse normale pour une question simple ;
- réponse détaillée pour une analyse ;
- réponse type cours pour préparer une séance ou un support pédagogique.

---

## 11. Rate limiting

Les API LLM ont des limites de requêtes.  
Le projet doit donc limiter les appels trop fréquents.

Principe prévu :

- compter le nombre de requêtes utilisateur ;
- imposer un délai minimal entre deux requêtes ;
- afficher un message clair si la limite est atteinte ;
- éviter d’envoyer inutilement une requête à Groq.

Exemple de message attendu :

```txt
Vous avez envoyé trop de requêtes en peu de temps. Merci d’attendre quelques secondes avant de réessayer.
```

Statut actuel :

```txt
Partiellement prévu / à finaliser.
```

Le projet peut déjà gérer certains timeouts et erreurs API, mais le rate limiting complet avec compteur et délai doit être renforcé.

---

## 12. Gestion des erreurs

La robustesse de l’application repose sur une gestion propre des erreurs.

Erreurs prises en compte ou à prendre en compte :

| Type d’erreur | Gestion attendue |
|---|---|
| Backend indisponible | Message utilisateur clair dans Streamlit |
| Timeout | Message indiquant que le backend met trop longtemps à répondre |
| Erreur API Groq | Message d’erreur propre, sans traceback brut |
| Réponse vide | Message indiquant qu’aucune réponse exploitable n’a été produite |
| Question vide | Blocage côté interface avec message utilisateur |
| Base documentaire vide | Message indiquant que le corpus doit être ingéré |
| Mauvaise requête | Retour HTTP propre côté backend |

Objectif : éviter d’afficher à l’utilisateur une erreur Python brute.

---

## 13. Monitoring et métriques

Le projet doit permettre de suivre le fonctionnement du chatbot.

Métriques techniques possibles :

- nombre total de requêtes ;
- temps de réponse moyen ;
- nombre d’erreurs ;
- nombre de timeouts ;
- nombre de chunks récupérés ;
- score moyen des sources récupérées.

Métriques fonctionnelles ou business simulées :

- nombre de questions posées ;
- types de questions ;
- modes les plus utilisés ;
- niveau de détail le plus utilisé ;
- satisfaction utilisateur simulée ;
- nombre de conversations créées.

Statut actuel :

```txt
Les conversations et messages sont stockés en base.
Les métriques dédiées restent à améliorer.
```

Piste prévue :

- ajouter des logs structurés ;
- ajouter une table `metrics` ;
- afficher certaines métriques dans l’interface Streamlit ;
- ajouter des exemples de logs dans le rendu final.

---

## 14. Amélioration UX

Améliorations déjà réalisées :

- interface Streamlit plus claire ;
- affichage sous forme de conversation ;
- historique de conversation ;
- possibilité de charger une conversation existante ;
- bouton pour créer une nouvelle conversation ;
- affichage des sources ;
- choix du mode de réponse ;
- choix du niveau de détail.

Améliorations prévues :

- bouton reset complet ;
- export d’une conversation ;
- meilleur affichage des sources ;
- ajout d’un indicateur de chargement plus précis ;
- affichage des métriques ;
- choix dynamique de la température ;
- choix dynamique du modèle ;
- gestion multi-utilisateur simple.

---

## 15. Installation locale

### 15.1 Prérequis

- Python 3.12 ;
- Docker ;
- Docker Compose ;
- une clé API Groq ;
- Git.

### 15.2 Cloner le projet

```bash
git clone https://github.com/USERNAME/meyer-rag-chatbot.git
cd meyer-rag-chatbot
```

### 15.3 Créer l’environnement virtuel

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 15.4 Installer les dépendances backend

```bash
cd backend
pip install -r requirements.txt
```

### 15.5 Configurer les variables d’environnement

Copier le fichier d’exemple :

```bash
cp .env.example .env
```

Puis modifier :

```env
DATABASE_URL=postgresql+psycopg://meyer:meyer_password@localhost:5432/meyer_rag
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
EMBEDDING_MODEL=intfloat/multilingual-e5-base
EMBEDDING_DIM=768
DATA_DIR=../data
```

### 15.6 Lancer PostgreSQL

Depuis la racine du projet :

```bash
docker compose up -d db
```

### 15.7 Ingestion du corpus

Depuis le dossier `backend/` :

```bash
python -m app.scripts.ingest_corpus
```

Cette commande :

- lit les documents dans `data/` ;
- découpe les documents en chunks ;
- génère les embeddings ;
- stocke les documents et chunks en base.

### 15.8 Lancer le backend

Depuis `backend/` :

```bash
python -m uvicorn app.main:app --reload
```

Backend :

```txt
http://localhost:8000
```

Swagger :

```txt
http://localhost:8000/docs
```

### 15.9 Lancer le frontend

Depuis la racine du projet :

```bash
streamlit run frontend/streamlit_app.py
```

Interface :

```txt
http://localhost:8501
```

---

## 16. Lancement avec Docker Compose

Le projet peut être lancé avec Docker Compose.

Services utilisés :

```txt
db        PostgreSQL + pgvector
backend   FastAPI
frontend  Streamlit
```

### 16.1 Construire et lancer les conteneurs

```bash
docker compose up --build
```

Ou en arrière-plan :

```bash
docker compose up -d --build
```

### 16.2 Lancer l’ingestion dans Docker

```bash
docker compose exec backend python -m app.scripts.ingest_corpus
```

### 16.3 Vérifier l’état de la base

```txt
http://localhost:8000/documents/stats
```

### 16.4 Accéder à l’application

Frontend :

```txt
http://localhost:8501
```

Backend :

```txt
http://localhost:8000/docs
```

### 16.5 Arrêter l’application

```bash
docker compose down
```

### 16.6 Réinitialiser totalement la base

```bash
docker compose down -v
```

Attention : cette commande supprime les données PostgreSQL.

---

## 17. Scripts et Makefile

Des scripts peuvent être utilisés pour simplifier les commandes.

### 17.1 Lancer l’application

```bash
./scripts/start_app.sh
```

### 17.2 Arrêter l’application

```bash
./scripts/stop_app.sh
```

### 17.3 Réinitialiser l’application

```bash
./scripts/reset_app.sh
```

### 17.4 Commandes Makefile

```bash
make start
make ingest
make logs-backend
make stop
```

---

## 18. Déploiement possible

Le sujet demande un déploiement sur Streamlit Cloud.  
Cependant, l’architecture actuelle contient trois composants :

```txt
Streamlit frontend
FastAPI backend
PostgreSQL + pgvector
```

Streamlit Cloud est adapté pour héberger une application Streamlit, mais il ne permet pas de lancer directement toute une architecture Docker Compose avec PostgreSQL et FastAPI.

Deux stratégies sont donc possibles.

### 18.1 Option simple pour le TP

Créer une version simplifiée où Streamlit contient directement la logique principale du chatbot.

Avantage :

- plus simple à déployer sur Streamlit Cloud ;
- conforme à la demande d’une URL Streamlit.

Limite :

- moins robuste ;
- moins proche de l’architecture actuelle ;
- moins adaptée à une vraie application complète.

### 18.2 Option plus propre

Déployer séparément :

```txt
Streamlit Cloud      → frontend
Render / Railway     → backend FastAPI
Supabase / Railway   → PostgreSQL + pgvector
Groq                 → modèle LLM
```

Dans ce cas, Streamlit Cloud appelle le backend via une URL publique :

```python
API_URL = "https://url-du-backend-deploye.com"
```

Cette solution est plus réaliste pour une application complète.

### 18.3 Option VPS

Déployer tout le projet sur un serveur avec Docker Compose :

```bash
docker compose up -d --build
docker compose exec backend python -m app.scripts.ingest_corpus
```

Avantage :

- conserve l’architecture actuelle ;
- simple à reproduire ;
- adapté à une démonstration complète.

Limite :

- nécessite de gérer un serveur.

---

## 19. Ce qui fonctionne actuellement

Fonctionnalités opérationnelles :

- backend FastAPI ;
- frontend Streamlit ;
- base PostgreSQL avec pgvector ;
- ingestion du corpus ;
- découpage en chunks ;
- génération d’embeddings ;
- stockage en base ;
- recherche vectorielle ;
- appel Groq ;
- affichage des sources ;
- conversations sauvegardées ;
- historique visible dans l’interface ;
- modes de réponse ;
- choix de la verbosité ;
- lancement local ;
- lancement Docker Compose.

---

## 20. Limites actuelles

### 20.1 Qualité variable du retrieval

La qualité de la réponse dépend des chunks récupérés.  
Pour les questions très générales, le système peut parfois récupérer des passages trop techniques.

### 20.2 Corpus multilingue difficile

Le corpus contient de l’allemand ancien, de l’anglais et du français.  
La recherche sémantique peut donc être moins précise qu’avec un corpus homogène.

### 20.3 Découpage encore perfectible

Les PDF sont ingérés page par page.  
Cela fonctionne, mais cela crée beaucoup de documents secondaires.

### 20.4 Rate limiting incomplet

Le rate limiting doit encore être renforcé avec :

- compteur ;
- délai entre requêtes ;
- message utilisateur clair.

### 20.5 Monitoring incomplet

Les conversations sont stockées, mais les métriques ne sont pas encore toutes structurées dans une table dédiée.

### 20.6 Déploiement non finalisé

Le projet fonctionne en local et avec Docker Compose.  
Le déploiement public reste à finaliser.

### 20.7 Pas encore de vraie gestion multi-utilisateur

Les conversations sont sauvegardées, mais elles ne sont pas encore séparées par compte utilisateur.

---

## 21. Pistes d’amélioration

### 21.1 Améliorer le retrieval

Ajouter une recherche hybride :

- recherche vectorielle ;
- recherche par mots-clés ;
- pondération par type de source ;
- priorité aux sources primaires ;
- re-ranking des chunks.

### 21.2 Ajouter des filtres

Filtres possibles :

```txt
sources primaires seulement
traductions seulement
PDF français seulement
préfaces et contexte
techniques uniquement
```

### 21.3 Améliorer la mémoire conversationnelle

Utiliser les derniers messages de la conversation dans le prompt pour mieux comprendre les questions de suivi.

Exemple :

```txt
Fais-moi une version plus courte.
```

### 21.4 Ajouter le choix dynamique de température

Permettre à l’utilisateur de choisir :

```txt
0
0.5
1
```

Puis comparer les réponses obtenues.

### 21.5 Ajouter le choix dynamique du modèle

Prévoir une interface pour choisir entre :

```txt
Groq
OpenAI
autre modèle compatible
```

### 21.6 Ajouter un vrai module de métriques

Créer une table dédiée pour stocker :

- temps de réponse ;
- erreurs ;
- mode utilisé ;
- nombre de sources ;
- satisfaction utilisateur simulée.

### 21.7 Exporter les conversations

Ajouter un export :

- Markdown ;
- JSON ;
- PDF.

### 21.8 Améliorer l’interface

Créer une interface plus professionnelle :

- meilleure sidebar ;
- meilleurs blocs de sources ;
- affichage des métriques ;
- bouton reset clair ;
- gestion multi-utilisateur basique.

---

## 22. Exemples de questions

Exemples de questions utilisables dans l’application :

```txt
Que dit Meyer sur le Vor et le Nach ?
```

```txt
Explique-moi le Zwerchhau pour un débutant.
```

```txt
Crée un drill de 10 minutes sur le Krumphau.
```

```txt
Meyer propose-t-il une escrime de jeu ou une escrime pour la vie ?
```

```txt
Fais-moi une fiche pédagogique sur le Fort et le Faible.
```

---

## 23. Exemple de logs attendus

Exemple de logs techniques possibles :

```txt
[INFO] Nouvelle requête reçue
[INFO] Mode utilisé : explanation
[INFO] Verbosité : detailed
[INFO] Chunks récupérés : 6
[INFO] Temps de retrieval : 0.42s
[INFO] Temps total de réponse : 4.85s
[INFO] Réponse envoyée avec succès
```

Exemple d’erreur gérée :

```txt
[ERROR] Timeout Groq API
[USER MESSAGE] Le modèle met trop longtemps à répondre. Merci de réessayer dans quelques instants.
```

---

## 24. Conclusion

Ce projet est une évolution d’un chatbot simple vers une application RAG plus robuste.

Il intègre :

- une architecture backend/frontend ;
- une base PostgreSQL ;
- une recherche vectorielle ;
- un corpus documentaire réel ;
- une interface conversationnelle ;
- une sauvegarde des conversations ;
- plusieurs modes de réponse ;
- une première réflexion sur la robustesse, le monitoring, les erreurs et le déploiement.

La version actuelle est fonctionnelle en local et avec Docker Compose.  
Les prochaines améliorations porteront principalement sur le rate limiting, le monitoring, le déploiement public, le choix dynamique de la température et l’amélioration de la qualité des réponses.
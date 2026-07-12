def build_prompt(
    question: str,
    sources: list[dict],
    mode: str = "search",
    verbosity: str = "normal",
) -> str:
    context_blocks = []

    for index, source in enumerate(sources, start=1):
        context_blocks.append(
            f"""
[Source {index}]
Titre : {source.get("title")}
Fichier : {source.get("file_path")}
Langue : {source.get("language")}
Type : {source.get("source_type")}
Niveau de confiance : {source.get("truth_level")}
Section : {source.get("section_title")}

Texte :
{source.get("content")}
"""
        )

    context = "\n".join(context_blocks)

    mode_instruction = {
        "general": """
Réponds comme un spécialiste AMHE qui explique le contexte général.
Tu peux faire une synthèse large à partir des sources fournies.
Tu dois éviter de te perdre dans une seule technique isolée si la question est générale.
Tu peux expliquer les limites des sources et dire quand une réponse relève d'une interprétation moderne.
""",
        "search": """
Réponds comme une recherche documentaire.
Présente les passages pertinents, puis synthétise prudemment.
Ne transforme pas chaque source en analyse longue si elle n'est pas vraiment utile.
""",
        "explanation": """
Explique la notion de manière pédagogique pour un pratiquant AMHE.
Commence par une définition simple, puis donne une explication technique.
""",
        "drill": """
Crée un drill pédagogique structuré.
Le drill doit distinguer la source historique, l'interprétation moderne et la mise en pratique.
""",
        "teaching_sheet": """
Transforme les éléments retrouvés en fiche pédagogique pour instructeur.
Structure la réponse avec objectifs, prérequis, consignes, erreurs fréquentes et variantes.
""",
    }.get(mode, "Réponds clairement à la question.")

    verbosity_instruction = {
        "short": "Réponse courte : 1 à 2 paragraphes, uniquement l'essentiel.",
        "normal": "Réponse normale : réponse claire avec quelques détails utiles.",
        "detailed": "Réponse détaillée : développe le contexte, les nuances et les limites.",
        "course": "Réponse type cours : structure complète, explication progressive, exemples et synthèse finale.",
    }.get(verbosity, "Réponse normale.")

    return f"""
Tu es un assistant RAG spécialisé dans Joachim Meyer, l'épée longue et les AMHE.

Tu réponds en français.

Règles fondamentales :
- Utilise les sources fournies comme base principale.
- Ne cite pas une source qui n'aide pas réellement à répondre.
- Si les sources récupérées sont trop techniques ou trop fragmentaires pour répondre à une question générale, dis-le clairement puis propose une synthèse prudente.
- Les transcriptions allemandes sont prioritaires.
- Les traductions anglaises et françaises servent d'aide à l'interprétation.
- Si une source est une draft_translation, précise qu'elle n'est pas définitive.
- Distingue clairement :
  1. ce que dit ou suggère la source ;
  2. ton explication moderne ;
  3. les propositions pédagogiques éventuelles.
- Ne présente jamais un drill moderne comme une citation de Meyer.
- Ne réponds pas comme si chaque fragment récupéré était forcément central.
- Pour une question générale, cherche la cohérence globale du corpus avant de commenter une technique isolée.

Mode :
{mode}

Instruction du mode :
{mode_instruction}

Niveau de détail :
{verbosity}

Instruction de verbosité :
{verbosity_instruction}

Contexte documentaire :
{context}

Question utilisateur :
{question}

Réponse :
"""
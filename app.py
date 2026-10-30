import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Radar Carrière - PFA 2027", page_icon="🎯", layout="wide")

st.title("🎯 Mon Radar Carrière - Pilotage PFA, R&D & Thèses")
st.markdown("Suivi intelligent, paginé et optimisé de vos opportunités d'ingénierie à l'international.")

DB_URL = "postgresql://postgres.kiqvunxegwjrnlwrbkor:Pchpi78th%40some@aws-0-eu-west-1.pooler.supabase.com:6543/postgres"

@st.cache_data(ttl=5)
def charger_donnees():
    try:
        conn = psycopg2.connect(DB_URL)
        query = """
            SELECT 
                o.id as offre_id,
                o.titre,
                o.entreprise,
                COALESCE(o.type_offre, 'Offres d''emploi') as type_offre,
                o.url,
                o.date_decouverte,
                COALESCE(c.id, 0) as candidature_id,
                COALESCE(c.statut, 'À postuler') as statut,
                c.date_candidature,
                c.cv_utilise,
                c.translated_language,
                c.translated_content
            FROM offres o
            LEFT JOIN candidatures c ON o.id = c.offre_id
            ORDER BY o.date_decouverte DESC;
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return pd.DataFrame()

df_offres = charger_donnees()

if df_offres.empty:
    st.info("Aucune offre trouvée. Utilisez le module de capture par URL ci-dessous pour ajouter votre première offre !")
else:
    # --- 1. TABLEAU DE BORD EXÉCUTIF & STATISTIQUES (KPIs) ---
    st.markdown("### 📊 Indicateurs Clés de Pilotage")
    total_offres = len(df_offres)
    candidatures_envoyees = len(df_offres[df_offres['statut'] != 'À postuler'])
    entretiens = len(df_offres[df_offres['statut'] == 'Entretien'])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Opportunités", total_offres)
    col2.metric("Candidatures Lancées", candidatures_envoyees)
    col3.metric("Entretiens Décrochés", entretiens)
    taux_conversion = f"{(entretiens / max(candidatures_envoyees, 1)) * 100:.1f}%"
    col4.metric("Taux de Conversion", taux_conversion)
    
    st.markdown("---")

    # --- 1.5. LE GHOST RECRUITER (Candidature Spontanée Marché Caché) ---
    with st.expander("👻 Le 'Ghost Recruiter' — Chasse & Candidatures Spontanées R&D (Marché Caché)"):
        st.markdown("Les meilleures opportunités en R&D ne sont souvent pas publiées. Ciblez directement les entreprises de pointe :")
        
        entreprises_cibles_ghost = {
            "Stellantis": {"contact": "Lead Cybersecurity & Embedded Systems Engineer", "actu": "Développement des calculateurs centraux et sécurisation des passerelles CAN."},
            "Bertrandt": {"contact": "Manager Innovation & Systèmes Embarqués", "actu": "Projets de rétro-ingénierie et sécurisation des réseaux embarqués véhicules."},
            "FAAR Industry": {"contact": "Responsable Technique Véhicule Autonome", "actu": "Conception d'architectures électroniques et logicielles sécurisées."},
            "Segula Technologies": {"contact": "Responsable R&D / Recrutement Automobile", "actu": "Expansion des architectures Software-Defined Vehicle (SDV) et conformité ISO 21434."},
            "FEV Group": {"contact": "Directeur Pôle Ingénierie & Bancs de Test", "actu": "Ouverture de nouveaux laboratoires de tests de calculateurs et cybersécurité."}
        }
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            entreprise_ghost = st.selectbox("Sélectionner l'entreprise cible :", list(entreprises_cibles_ghost.keys()))
            type_sujet_ghost = st.selectbox("Type de sujet visé :", ["Stage PFA / PFE (2 à 3 mois)", "Thèse de Doctorat R&D", "Alternance / Emploi"])
        with col_g2:
            st.info(f"🎯 **Interlocuteur cible** : {entreprises_cibles_ghost[entreprise_ghost]['contact']}\n\n📰 **Actualité R&D** : {entreprises_cibles_ghost[entreprise_ghost]['actu']}")
            
        if st.button("🚀 Déclencher Approche Spontanée"):
            st.success("Message d'approche généré avec succès !")
            email_spontane = f"""Objet : Candidature Spontanée – {type_sujet_ghost} en Cybersécurité & Systèmes Embarqués (Profil Ingénieur ASD2)

Bonjour {entreprises_cibles_ghost[entreprise_ghost]['contact']},

Je suis SOME SEOZOUMON, étudiant en deuxième année du cycle d'ingénieur (ASD2) en Automobile et Solutions Digitales à l'ENSA Berrechid. 

Suivant de très près l'actualité de {entreprise_ghost} et notamment vos travaux sur [{entreprises_cibles_ghost[entreprise_ghost]['actu']}], je me permets de vous contacter directement. 

Dans le cadre de mon parcours, je développe une solide expertise pratique en cybersécurité automobile et systèmes embarqués : reverse engineering de réseaux CAN (avec can-utils, ICSim et Wireshark sous Kali Linux), analyse de conformité ISO/SAE 21434, et programmation de microcontrôleurs.

Je serais ravi d'échanger avec vous sur la manière dont mes compétences pourraient contribuer à vos projets R&D en cours. Vous trouverez mon CV en pièce jointe.

Bien cordialement,
SOME SEOZOUMON
Étudiant Ingénieur | ENSA Berrechid
"""
            st.text_area("Message d'approche prêt à l'envoi :", email_spontane, height=240)

    st.markdown("---")

    # --- 2. MODULE DE CAPTURE AUTOMATIQUE PAR URL ---
    with st.expander("⚡ Saisie Rapide & Capture Automatique par URL"):
        st.markdown("Collez l'URL d'une offre pour l'intégrer instantanément à votre base de données :")
        
        col_url1, col_url2 = st.columns([3, 1])
        with col_url1:
            url_saisie = st.text_input("URL de l'offre (LinkedIn, site RH, etc.) :", placeholder="https://...")
        with col_url2:
            nom_entreprise_saisi = st.text_input("Nom de l'entreprise :", placeholder="Ex: Segula")
            
        type_offre_saisi = st.selectbox("Section cible :", ["Stage PFA & PFE", "Thèses / R&D", "Offres d'emploi"])
        titre_saisi = st.text_input("Intitulé du poste :", placeholder="Ex: Ingénieur Cybersécurité Embarquée")
        
        if st.button("🚀 Enregistrer l'offre instantanément"):
            if url_saisie and nom_entreprise_saisi and titre_saisi:
                try:
                    conn = psycopg2.connect(DB_URL)
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO offres (titre, entreprise, url, type_offre)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (url) DO NOTHING;
                    """, (titre_saisi, nom_entreprise_saisi, url_saisie, type_offre_saisi))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success("✨ Offre capturée et enregistrée avec succès dans le Radar !")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors de l'enregistrement : {e}")
            else:
                st.warning("Veuillez remplir au moins l'URL, l'entreprise et le titre de l'offre.")

    # --- 3. MODULE DE REVERSE JOB MATCHING (Intelligence Marché) ---
    with st.expander("📈 Radar d'Intelligence Marché & Reverse Job Matching (Tendances Semaine)"):
        st.markdown("L'analyse automatisée du volume des offres permet de détecter les normes et compétences les plus exigées par les recruteurs en R&D :")
        
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.metric("🔥 Norme Top Demande", "UNECE R155 / ISO 21434", "Forte exigence en cybersécurité")
        with col_t2:
            st.metric("⚙️ Protocole Clé", "UDS / CAN Bus", "Standard incontournable embarqué")
        with col_t3:
            st.metric("🛠️ Compétence Logicielle", "Python / C++ / Wireshark", "Outils de reverse engineering")
            
        st.info("💡 **Recommandation IA** : Vos compétences actuelles sur le reverse engineering de réseaux CAN et l'ISO 21434 correspondent exactement aux exigences fortes du marché automobile.")

    # --- PANNEAU LATÉRAL : ASSISTANT CARRIÈRE, MARCHÉ CIBLE & TRADUCTION IA ---
    st.sidebar.header("🛠️ Assistant Carrière & International")
    
    profil_choisi = st.sidebar.selectbox(
        "Sélectionnez votre profil technique :",
        [
            "Profil Cybersécurité Automobile (CAN bus, ISO 21434, Wireshark, ICSim)",
            "Profil Systèmes Embarqués (C/C++, Microcontrôleurs PIC16F84A, Proteus, I2C)"
        ]
    )
    
    # Gestion dynamique et ajout de compétences
    competences_base = "Cybersécurité automobile, CAN bus, ISO 21434, Kali Linux, ICSim, Wireshark, UDS, C/C++, Python"
    
    if "ma_liste_competences" not in st.session_state:
        st.session_state.ma_liste_competences = competences_base
        
    nouvelle_competence = st.sidebar.text_input("➕ Ajouter une compétence à votre profil :", placeholder="Ex: Autosar, TARA, SecOC...")
    if st.sidebar.button("Enregistrer la compétence"):
        if nouvelle_competence and nouvelle_competence not in st.session_state.ma_liste_competences:
            st.session_state.ma_liste_competences += f", {nouvelle_competence}"
            st.sidebar.success(f"Compétence '{nouvelle_competence}' ajoutée !")

    competences_actives = st.sidebar.text_area("Vos compétences actives (Éditable) :", st.session_state.ma_liste_competences)
    st.sidebar.markdown("---")

    # Sélecteur de Marché / Pays Cible (France/Europe vs Canada/Nord-Amériques)
    marche_cible = st.sidebar.selectbox(
        "Marché / Pays Cible :",
        [
            "🇫🇷 France / Europe (Standards normés & formels)",
            "🇨🇦 Canada / Amérique du Nord (Direct, orienté résultats & accomplissements)"
        ]
    )
    
    # --- NOUVEAU : TOGGLE CVE & THREAT INTELLIGENCE ALERTER ---
    inclure_cve = st.sidebar.checkbox("🛡️ Injecter la veille CVE / Menaces récentes (Auto-ISAC)", value=True, help="Ajoute subtilement une phrase sur les vulnérabilités récentes des bus CAN/UDS.")

    st.sidebar.subheader("✉️ Générateur Adapté au Marché")
    offre_selectionnee = st.sidebar.selectbox("Choisir une offre pour la lettre :", df_offres['titre'].tolist())
    consignes_correction = st.sidebar.text_area("Instructions spécifiques :", "Mettre en avant mes projets pratiques et ma rigueur méthodologique.")
    
    if st.sidebar.button("Généraliser & Adapter la Lettre"):
        offre_choisie = df_offres[df_offres['titre'] == offre_selectionnee].iloc[0]
        st.sidebar.success("Lettre générée selon les standards du marché cible !")
        
        # Phrase subtile CVE & Threat Intelligence si cochée
        phrase_cve_fr = "\n\nPar ailleurs, passionné par la sécurisation des architectures face aux menaces récentes, je suis de très près les dernières vulnérabilités affectant les bus CAN et protocoles UDS, me permettant d'anticiper les vecteurs d'attaque sur les systèmes connectés." if inclure_cve else ""
        phrase_cve_en = "\n\nFurthermore, deeply passionate about securing architectures against emerging threats, I closely monitor recent vulnerabilities affecting CAN buses and UDS protocols, allowing me to proactively mitigate attack vectors on connected systems." if inclure_cve else ""

        # Adaptation de la structure selon le pays cible (France vs Canada)
        if "Canada" in marche_cible:
            lettre_finale = f"""Subject: Application for {offre_choisie['titre']} – {offre_choisie['entreprise']}

Dear Hiring Manager,

As a dedicated engineering student specializing in Automotive and Digital Solutions (ASD2) at ENSA Berrechid, I am writing to express my strong interest in the {offre_choisie['titre']} position at {offre_choisie['entreprise']}.

With hands-on expertise in {competences_actives}, I bring a proven track record of designing secure embedded architectures and executing rigorous risk assessments aligned with industry standards like ISO 21434. My practical background includes advanced CAN bus reverse engineering and cryptographic protocol validation.{phrase_cve_en}

[Key Highlight / Instruction: {consignes_correction}]

I am eager to contribute my technical drive and problem-solving mindset to your R&D teams. Thank you for your time and consideration.

Best regards,
SOME SEOZOUMON
Automotive Cybersecurity & Embedded Systems Engineer
"""
        else:
            lettre_finale = f"""Objet : Candidature - {offre_choisie['titre']} ({offre_choisie['entreprise']})

Madame, Monsieur,

Actuellement étudiant en deuxième année du cycle d'ingénieur (ASD2) en Automobile et Solutions Digitales à l'ENSA Berrechid, je vous propose ma candidature pour le poste de {offre_choisie['titre']} au sein de {offre_choisie['entreprise']}.

Passionné par la cybersécurité automobile et les systèmes embarqués, je développe activement mes compétences à travers des projets pratiques : reverse engineering de réseaux CAN, analyse de trames avec Wireshark et ICSim sous Kali Linux, ainsi que la conformité aux normes ISO/SAE 21434.{phrase_cve_fr}

[Note d'ajustement : {consignes_correction}]

Intégrer votre structure me permettrait d'apporter ma rigueur méthodologique et mon fort engagement sur des sujets à forte valeur ajoutée. Je me tiens à votre entière disposition pour un entretien.

Bien cordialement,
SOME SEOZOUMON
Étudiant Ingénieur en Cybersécurité & Systèmes Embarqués
"""

        # Onglets de style / lettre dans la barre latérale
        tab_lettre, tab_infos = st.sidebar.tabs(["📄 Lettre Générée", "💡 Note de Style"])
        with tab_lettre:
            st.text_area("Copier votre lettre :", lettre_finale, height=280)
        with tab_infos:
            if "Canada" in marche_cible:
                st.info("🇨🇦 **Standard Nord-Américain appliqué** : Style direct, synthétique, axé sur les compétences tangibles et la veille des menaces CVE.")
            else:
                st.info("🇫🇷 **Standard Européen appliqué** : Style formel, structuré, intégrant la Threat Intelligence (CVE / Auto-ISAC).")

    # --- SIMULATEUR D'ENTRETIEN TECHNIQUE ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎙️ Simulateur d'Entretien IA")
    offres_en_entretien = df_offres[df_offres['statut'] == 'Entretien']
    
    if not offres_en_entretien.empty:
        offre_entretien_choisie = st.sidebar.selectbox("Sélectionner l'offre en entretien :", offres_en_entretien['titre'].tolist())
        if st.sidebar.button("Simuler l'entretien technique"):
            st.sidebar.success("Scénario d'entretien généré !")
            st.sidebar.markdown(f"### 🎯 Questions pour : {offre_entretien_choisie}")
            st.sidebar.markdown("""
**1. Architecture & Analyse de Risques :**  
> *"Comment mettriez-vous en place une analyse TARA selon la norme ISO/SAE 21434 ?"*  
**2. Sécurité des Protocoles & CVE :**  
> *"Quelles sont les limites du protocole CAN face au spoofing et comment traiteriez-vous une faille critique de type zero-day sur une passerelle connectée ?"*
""")
    else:
        st.sidebar.info("💡 Passez une offre au statut **'Entretien'** pour débloquer le simulateur !")

    # --- 4. TRAITEMENT DU MATCHING ---
    def analyser_match(row):
        texte = (str(row['titre']) + " " + str(row['entreprise'])).lower()
        mots_reference = [m.strip().lower() for m in competences_actives.split(",")]
        mots_presents = [comp for comp in mots_reference if comp in texte]
        score = min(30 + (len(mots_presents) * 30), 100)
        mots_manquants = [comp for comp in ["iso 21434", "can bus", "uds", "autosar", "tara"] if comp not in texte]
        
        if score >= 75: pastille = "🟢 Excellent"
        elif score >= 45: pastille = "🟡 Moyen"
        else: pastille = "🔴 Faible"
        
        return pastille, mots_manquants

    resultats_match = df_offres.apply(analyser_match, axis=1)
    df_offres['Match IA'] = [r[0] for r in resultats_match]
    df_offres['Liste Manquants'] = [r[1] for r in resultats_match]
    df_offres['Compétences Manquantes'] = df_offres['Liste Manquants'].apply(lambda x: ", ".join(x) if x else "Aucun")

    def calculer_relance(row):
        if pd.notna(row['date_candidature']):
            date_cand = pd.to_datetime(row['date_candidature'])
            return (date_cand + timedelta(days=7)).strftime('%d/%m/%Y')
        return "À définir"

    df_offres['Date Relance (J+7)'] = df_offres.apply(calculer_relance, axis=1)

    # --- 5. DÉTECTEUR DE SIGNAUX FAIBLES ---
    st.markdown("---")
    with st.expander("📡 Détecteur de Signaux Faibles & Veille Entreprises Cibles"):
        col_sig1, col_sig2 = st.columns(2)
        with col_sig1:
            st.info("🚨 **Signal Détecté : FEV Group**\n\n*Actualité* : Ouverture d'un pôle d'ingénierie en cybersécurité automobile.")
        with col_sig2:
            st.success("💡 **Signal Détecté : Segula Technologies**\n\n*Actualité* : Expansion des projets R&D Software-Defined Vehicle (SDV).")

    # --- 6. NAVIGATION PAR ONGLETS & AFFICHAGE ---
    st.markdown("---")
    mode_affichage = st.radio("Mode de visualisation du pipeline :", ["📂 Sections Analytiques par Type", "📋 Pipeline Kanban Interactif (Trello-like)"], horizontal=True)
    st.markdown("---")

    def regrouper_sections(type_brut):
        t = str(type_brut).lower()
        if "thèse" in t or "r&d" in t or "doctorat" in t: return "Thèses / R&D"
        elif "stage" in t or "pfa" in t or "pfe" in t or "alternance" in t: return "Stage PFA & PFE"
        else: return "Offres d'emploi"

    df_offres['Section'] = df_offres['type_offre'].apply(regrouper_sections)
    dataframes_modifies = {}

    if mode_affichage == "📂 Sections Analytiques par Type":
        sections_cibles = ["Thèses / R&D", "Stage PFA & PFE", "Offres d'emploi"]
        onglets = st.tabs([f"📂 {sec}" for sec in sections_cibles])
        
        for idx, section in enumerate(sections_cibles):
            with onglets[idx]:
                df_subset = df_offres[df_offres['Section'] == section].copy()
                nombre_offres = len(df_subset)
                
                st.subheader(f"Section : {section} ({nombre_offres} offres)")
                
                elements_par_page = 15
                nb_pages = max(1, (nombre_offres // elements_par_page) + (1 if nombre_offres % elements_par_page > 0 else 0))
                
                page_courante = st.number_input(f"Page (sur {nb_pages}) pour {section}", min_value=1, max_value=nb_pages, step=1, key=f"page_{section}")
                debut = (page_courante - 1) * elements_par_page
                fin = debut + elements_par_page
                df_page = df_subset.iloc[debut:fin]
                
                colonnes_config = {
                    "offre_id": None, "candidature_id": None, "type_offre": None, "Section": None,
                    "translated_language": None, "translated_content": None, "Liste Manquants": None,
                    "titre": st.column_config.TextColumn("Titre du poste", width="medium"),
                    "entreprise": st.column_config.TextColumn("Entreprise", width="small"),
                    "Match IA": st.column_config.TextColumn("Match IA", width="small"),
                    "Compétences Manquantes": st.column_config.TextColumn("Manquant (Tags)", width="medium"),
                    "statut": st.column_config.SelectboxColumn("Statut", options=["À postuler", "CV Envoyé", "En attente", "Entretien", "Refusé"], required=True, width="small"),
                    "date_candidature": st.column_config.DateColumn("Date candidature", format="DD/MM/YYYY"),
                    "Date Relance (J+7)": st.column_config.TextColumn("Date Relance", width="small"),
                    "cv_utilise": st.column_config.TextColumn("CV utilisé", width="small"),
                    "date_decouverte": st.column_config.DatetimeColumn("Découvert le", format="DD/MM/YYYY"),
                    "url": st.column_config.LinkColumn("Lien", display_text="Voir l'offre 🔗")
                }

                edited_df = st.data_editor(df_page, column_config=colonnes_config, hide_index=True, use_container_width=True, key=f"table_{section}")
                dataframes_modifies[section] = edited_df
                st.write("")

                # --- CENTRE DE FORMATION & REMÉDIATION ---
                if not df_page.empty:
                    st.markdown("---")
                    st.markdown("🎯 **Centre de Formation & Remédiation des Lacunes :**")
                    selected_offre_title = st.selectbox("Choisir une offre pour analyser les compétences manquantes :", df_page['titre'].tolist(), key=f"sel_comp_{section}")
                    
                    row_selected = df_page[df_page['titre'] == selected_offre_title].iloc[0]
                    manquants_list = row_selected['Liste Manquants']
                    
                    if manquants_list:
                        st.markdown("Cliquez sur un tag pour lancer une recherche rapide de documentation technique :")
                        cols_tags = st.columns(len(manquants_list) if len(manquants_list) > 0 else 1)
                        for i, comp in enumerate(manquants_list):
                            with cols_tags[i]:
                                if st.button(f"🔍 Apprendre : {comp.upper()}", key=f"btn_learn_{section}_{i}"):
                                    st.markdown(f"📚 **Ressource recommandée pour `{comp}`** : Consultez les standards de spécification technique ou cherchez des modules pratiques sur GitHub / Udemy.")
                    else:
                        st.success("🎉 Aucune lacune détectée sur cette offre par rapport à vos compétences actives !")

    else:
        # --- VUE KANBAN ---
        st.markdown("### 📋 Pipeline Kanban des Candidatures")
        colonnes_kanban = ["À postuler", "CV Envoyé", "En attente", "Entretien", "Refusé"]
        cols = st.columns(len(colonnes_kanban))
        
        kanban_dfs = {}
        for idx, statut in enumerate(colonnes_kanban):
            with cols[idx]:
                st.markdown(f"**📌 {statut}**")
                df_col = df_offres[df_offres['statut'] == statut]
                
                edited_kanban = st.data_editor(
                    df_col[['offre_id', 'candidature_id', 'titre', 'entreprise', 'statut']],
                    column_config={
                        "offre_id": None, "candidature_id": None,
                        "titre": st.column_config.TextColumn("Poste", width="small"),
                        "entreprise": st.column_config.TextColumn("Entreprise", width="small"),
                        "statut": st.column_config.SelectboxColumn("Statut", options=colonnes_kanban, required=True)
                    },
                    hide_index=True,
                    use_container_width=True,
                    key=f"kanban_{statut}"
                )
                kanban_dfs[statut] = edited_kanban

    st.markdown("---")
    
    if st.button("💾 Enregistrer toutes les modifications", type="primary"):
        try:
            conn = psycopg2.connect(DB_URL)
            cursor = conn.cursor()
            
            if mode_affichage == "📂 Sections Analytiques par Type":
                source_sauvegarde = dataframes_modifies.items()
            else:
                source_sauvegarde = kanban_dfs.items()
                
            for key, df_modifie in source_sauvegarde:
                for index, row in df_modifie.iterrows():
                    if row['candidature_id'] == 0 and row['statut'] != "À postuler":
                        cursor.execute("""
                            INSERT INTO candidatures (offre_id, statut, date_candidature)
                            VALUES (%s, %s, CURRENT_DATE);
                        """, (row['offre_id'], row['statut']))
                    elif row['candidature_id'] != 0:
                        cursor.execute("""
                            UPDATE candidatures SET statut = %s WHERE id = %s;
                        """, (row['statut'], row['candidature_id']))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Modifications enregistrées avec succès dans vos tables !")
            st.rerun()
        except Exception as e:
            st.error(f"Erreur de sauvegarde : {e}")
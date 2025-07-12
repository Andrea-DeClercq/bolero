export const ouvrageSearchConfig = {
  availableFields: [
    { key: "id", label: "ID" },
    { key: "sous_titre", label: "Sous-titre" },
    { key: "volume", label: "Volume" },
    { key: "ean", label: "EAN" },
    { key: "portail", label: "Portail" },
    { key: "auteur_nom", label: "Nom de l'auteur" },
    { key: "auteur_prenom", label: "Prénom de l'auteur" },
    { key: "id_auteur", label: "ID Auteur" },
    { key: "id_proprio", label: "ID Propriétaire" },
    { key: "traducteur", label: "Traducteur" },
    { key: "langue", label: "Langue" },
  ],
  fixedFields: {
    titre: "",
    editeur: "",
    anneeParution: ""
  }
};

export const recensionSearchConfig = {
  availableFields: [
      { key: "id", label: "ID" },
      { key: "portail", label: "Portail" },
      { key: "volume", label: "Volume" },
      { key: "numero", label: "Numéro" },
      { key: "date_parution", label: "Date de parution" },
      { key: "url", label: "URL" },
      { key: "auteur_nom", label: "Nom de l'auteur" },
      { key: "auteur_prenom", label: "Prénom de l'auteur" },
      { key: "id_auteur", label: "ID Auteur" },
      { key: "id_proprio", label: "ID Propriétaire" },
      { key: "traducteur", label: "Traducteur" },
      { key: "langue", label: "Langue" },
  ],
  fixedFields: {
      titre: "",
      titre_revue: "",
      annee: ""
    }
};  
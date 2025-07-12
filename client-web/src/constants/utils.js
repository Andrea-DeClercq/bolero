/**
 * Hydrate un ensemble de champs Vue ref à partir d'un objet source.
 *
 * @param {Object} source - L'objet de données source (ex: response.data)
 * @param {Map} fields - Une map { champRef: 'cléDansSource' } à hydrater
 * @param {any} fallback - Valeur par défaut si absente
 */
export function hydrateFields(source, mapping, fallback = '') {
  if (!(mapping instanceof Map)) return;

  for (const [refField, key] of mapping.entries()) {
      if (refField && typeof refField === 'object' && 'value' in refField) {
      refField.value = source?.[key] ?? fallback;
      }
  }
}
  

/**
 * Hydrate un champ Vue ref depuis un objet source.
 * 
 * @param {Ref} fieldRef - Le champ Vue à modifier (ex: titre, editeur...)
 * @param {Object} source - L'objet source (ex: response.data)
 * @param {string} key - La clé à lire depuis source
 * @param {any} fallback - La valeur par défaut si absente
 */
export function hydrateField(fieldRef, source, key, fallback = '') {
  fieldRef.value = source?.[key] ?? fallback;
}

export function generateId() {
  return crypto.randomUUID().split("-")[0]
}

// Permet d'afficher correctement les données d'un ouvrage dans la liste pour le formulaire de recension
export const normalizeOuvrage = (ouvrage) => ({
  id: ouvrage.id,
  titre: ouvrage.titre,
  sousTitre: ouvrage.sous_titre || ouvrage.sousTitre || null,
  editeur: ouvrage.editeur || null,
  anneeParution: ouvrage.annee_parution || ouvrage.anneeParution || null,
  idRelation: ouvrage.id_relation || ouvrage.idRelation || null,
});
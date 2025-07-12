export function useNavigation(router) {
  const goToHome = () => {
    router.push({ name: 'home' });
  };

  const goToLogin = () => {
    router.push({ name: 'login' });
  };

  const redirectToExternalUrl = (url) => {
    window.open(url, '_blank');
  };

  /*********************************************************************
   *                         ROUTES AUTEUR
   ********************************************************************/
  const goToAuteur = (id) => {
    router.push({ name: 'auteur', params: { id } });
  };

  const goToSearchAuteur = () => {
    router.push({ name: "auteurs-list" })
  };

  const goToAddAuteur = () => {
    router.push({ name: "auteur-new" })
  };

  const goToEditAuteur = () => {
    router.push({ name: "auteur-edit"})
  };

  /*********************************************************************
   *                         ROUTES OUVRAGE
   ********************************************************************/
  const goToOuvrage = (id) => {
    router.push({ name: 'ouvrage', params: { id } });
  };

  const goToSearchOuvrage = () => {
    router.push({ name: 'ouvrages-list'});
  };

  const goToAddOuvrage = () => {
    router.push({ name: 'ouvrage-new'});
  };

  const goToEditOuvrage = (id) => {
    router.push({ name: 'ouvrage-edit' });
  };

  /*********************************************************************
   *                         ROUTES RECENSION
   ********************************************************************/
  const goToRecension = (id) => {
    router.push({ name: 'recension', params: { id } });
  };

  const goToSearchRecension = () => {
    router.push({ name: 'recensions-list'});
  };

  const goToAddRecension = () => {
    router.push({ name: 'recension-new'});
  };
  
  const goToEditRecension = () => {
    router.push({ name: "recension-edit" })
  };

  return {
    goToHome,
    goToLogin,
    goToAuteur,
    goToAddAuteur,
    goToEditAuteur,
    goToSearchAuteur,
    goToOuvrage,
    goToAddOuvrage,
    goToEditOuvrage,
    goToSearchOuvrage,
    goToRecension,
    goToAddRecension,
    goToEditRecension,
    goToSearchRecension,
    redirectToExternalUrl,
  };
}

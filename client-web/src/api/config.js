// Configuration pour les routes qui nécessite une authentification avec formulaire
export const configureRequestForm = (token, params) => {
	const config = {
			headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'multipart/form-data'
			}
	};
	// La route utilise un multipart/form, donc je convertis mon JSON en formData
	const formData = new FormData();
	Object.keys(params).forEach(key => {
			if (params[key]) {
					formData.append(key, params[key])
			}
	});
	return { config, formData };
};

// Seulement le token pour l'authentification pour les routes DELETES
export const configureAuthRequest = (token) => {
	return {
			headers: {
			'Authorization': `Bearer ${token}`,
			'Content-Type': 'application/json'
			}
	};
};
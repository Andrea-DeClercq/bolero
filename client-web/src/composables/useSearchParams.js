export function useSearchParams() {
  function buildParams({ page = 1, limit = 100, sort = 'id', order = 'asc', fixedValues = {}, searchFields = [] }) {
      const params = {
      page,
      limit,
      sort,
      order
      };

    Object.entries(fixedValues).forEach(([key, value]) => {
      if (value && value.trim() !== '') {
        params[key === 'anneeParution' ? 'annee_parution' : key] = value;
      }
    });

    searchFields.forEach((field) => {
      if (field.key && field.value && field.value.trim() !== '') {
        params[field.key] = field.value;
      }
    });

    return params;
  }

  function buildExportParams({ fixedValues = {}, searchFields = [] }) {
    const params = {};
  
    Object.entries(fixedValues).forEach(([key, value]) => {
      if (value && value.trim() !== '') {
        params[key === 'anneeParution' ? 'annee_parution' : key] = value;
      }
    });
  
    searchFields.forEach((field) => {
      if (field.key && field.value && field.value.trim() !== '') {
        params[field.key] = field.value;
      }
    });
  
    return params;
  }

  return { buildParams, buildExportParams };
}  
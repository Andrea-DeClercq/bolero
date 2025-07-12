import { reactive, ref } from 'vue';

export function useSearchFields(availableFields, fixedFields) {
  const searchFields = ref([]);
  const fixedValues = reactive({ ...fixedFields });

  const addField = () => {
    searchFields.value.push({ key: "", value: "" });
  };

  const removeField = (index) => {
    searchFields.value.splice(index, 1);
  };

  const removeAllDynamicFields = () => {
    searchFields.value = [];
  };

  const removeAllFields = () => {
    removeAllDynamicFields();
    Reflect.ownKeys(fixedValues).forEach((key) => {
      fixedValues[key] = "";
    });
  };

  const filteredAvailableFields = (currentIndex) => {
    const selectedKeys = searchFields.value.map((field) => field.key);
    return availableFields.filter(
      (field) => 
        !selectedKeys.includes(field.key) ||
        searchFields.value[currentIndex]?.key === field.key
    );
  };

  const updateAvailableFields = () => {
    searchFields.value = [...searchFields.value];
  };

  return {
    searchFields,
    fixedValues,
    addField,
    removeField,
    removeAllDynamicFields,
    removeAllFields,
    filteredAvailableFields,
    updateAvailableFields
  };
}

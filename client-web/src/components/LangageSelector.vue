<script setup>
import { languesOptions } from "@/constants/langues";

const props = defineProps({
  modelValue: String,
});

const emit = defineEmits(["update:modelValue"]);
</script>

<template lang="pug">
select.form-select(@change="emit('update:modelValue', $event.target.value)" :value="modelValue")
  option(v-for="langue in languesOptions" :key="langue.code" :value="langue.code") {{ langue.label }}
</template>

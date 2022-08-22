<template>
  <span @click="click">info:{{ props.foo }}</span>
</template>

<script lang="ts" setup>
import { defineEmits, defineProps } from 'vue'

const emit = defineEmits(['change'])
const props = defineProps({ foo: String })
console.log(props)

const click = () => {
  emit('change', props.foo)
}
</script>
<style />

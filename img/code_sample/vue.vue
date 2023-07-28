<script lang="ts" setup>
const emit = defineEmits<{
  change: [foo: string]
}>()
const props = defineProps<{ foo: string }>()
console.log(props)

const clickBtn = () => emit('change', props.foo)
</script>

<template>
  <Transition>
    <span class="text-blue" @click="clickBtn()">
      info:{{ props.foo }}
    </span>
  </Transition>
</template>

<style>
.text-blue {
  color: blue;
}
</style>
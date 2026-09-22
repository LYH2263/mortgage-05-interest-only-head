<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
</script>
<template><div class="page"><h1>试算记录</h1>
<table>
  <tr><th>ID</th><th>时间</th><th>类型</th><th>贷款</th><th></th></tr>
  <tr v-for="h in items" :key="h.id">
    <td>#{{ h.id }}</td>
    <td>{{ h.created_at }}</td>
    <td>{{ h.kind }}</td>
    <td>{{ h.loan_id ?? '—' }}</td>
    <td><router-link :to="`/history/${h.id}`">打开旧条</router-link></td>
  </tr>
</table>
</div></template>

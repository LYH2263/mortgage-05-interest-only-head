<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const parse = (h) => {
  let input = {}, result = {}
  try { input = JSON.parse(h.input_json) } catch (e) { /* ignore */ }
  try { result = JSON.parse(h.result_json) } catch (e) { /* ignore */ }
  return { input, result }
}
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
</script>
<template><div class="page"><h1>试算记录</h1>
<table>
<tr><th>#</th><th>时间</th><th>类型</th><th>只息期数 K</th><th>月供</th></tr>
<tr v-for="h in items" :key="h.id">
  <td>#{{ h.id }}</td>
  <td>{{ h.created_at }}</td>
  <template v-if="parse(h).result.interest_only">
    <td>只息</td>
    <td>{{ parse(h).result.interest_only_months }}</td>
    <td>前{{ parse(h).result.interest_only_months }}期 {{ parse(h).result.monthly_payment_io }} · 之后 {{ parse(h).result.monthly_payment_after }}</td>
  </template>
  <template v-else>
    <td>等额本息</td>
    <td>—</td>
    <td>{{ parse(h).result.monthly_payment ?? '—' }}</td>
  </template>
</tr>
</table>
</div></template>

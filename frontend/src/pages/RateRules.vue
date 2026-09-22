<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, patchJSON } from '../api'
const items = ref([])
const name = ref('')
const k = ref(12)
const err = ref('')
const load = async () => { items.value = (await getJSON('/api/interest-only-rules')).items }
const create = async () => {
  err.value = ''
  try {
    if (k.value <= 0) { err.value = '只息期数 K 必须为正整数'; return }
    await postJSON('/api/interest-only-rules', { name: name.value || `只息${k.value}期`, interest_only_months: k.value })
    name.value = ''; k.value = 12
    await load()
  } catch (e) { err.value = String(e.message || e) }
}
const save = async (r) => {
  r._err = ''
  if (!(r.interest_only_months > 0)) { r._err = 'K 须为正整数'; return }
  try {
    const body = { name: r.name, interest_only_months: r.interest_only_months }
    await patchJSON(`/api/interest-only-rules/${r.id}`, body)
    await load()
  } catch (e) { r._err = String(e.message || e) }
}
const disable = async (r) => {
  await postJSON(`/api/interest-only-rules/${r.id}/disable`, {})
  await load()
}
const enable = async (r) => {
  await patchJSON(`/api/interest-only-rules/${r.id}`, { enabled: true })
  await load()
}
onMounted(load)
</script>
<template><div class="page"><h1>只息规则</h1>
<p>前 K 期只还利息、本金为零；其后按等额本息重算。试算时 K 须为正且小于总期数。</p>
<div class="rule-form">
  <input v-model="name" placeholder="规则名称" />
  <label>只息期数 K <input v-model.number="k" type="number" min="1" /></label>
  <button @click="create">新建规则</button>
  <span v-if="err" class="err">{{ err }}</span>
</div>
<table>
  <tr><th>ID</th><th>名称</th><th>只息期数 K</th><th>状态</th><th>操作</th></tr>
  <tr v-for="r in items" :key="r.id">
    <td>#{{ r.id }}</td>
    <td><input v-model="r.name" /></td>
    <td><input v-model.number="r.interest_only_months" type="number" min="1" /></td>
    <td>{{ r.enabled ? '启用' : '停用' }}</td>
    <td class="row-actions">
      <button @click="save(r)">保存</button>
      <button v-if="r.enabled" @click="disable(r)">停用</button>
      <button v-else @click="enable(r)">启用</button>
      <span v-if="r._err" class="err">{{ r._err }}</span>
    </td>
  </tr>
</table>
</div></template>
<style scoped>
.rule-form { display:flex; gap:0.5rem; align-items:center; margin:0.75rem 0; }
.row-actions { display:flex; gap:0.4rem; }
.err { color:#a33; }
</style>

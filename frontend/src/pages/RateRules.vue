<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, putJSON } from '../api'
const items = ref([])
const error = ref('')
const newName = ref('')
const newK = ref(12)
const editing = ref(null)
const editName = ref('')
const editK = ref(12)
const load = async () => { items.value = (await getJSON('/api/interest-only-rules')).items }
const create = async () => {
  error.value = ''
  try {
    await postJSON('/api/interest-only-rules', { name: newName.value || `只息${newK.value}期`, interest_only_months: newK.value, enabled: true })
    newName.value = ''; newK.value = 12
    await load()
  } catch (e) { error.value = e.message }
}
const startEdit = (r) => { editing.value = r.id; editName.value = r.name; editK.value = r.interest_only_months }
const saveEdit = async (r) => {
  error.value = ''
  try {
    await putJSON(`/api/interest-only-rules/${r.id}`, { name: editName.value, interest_only_months: editK.value, enabled: r.enabled })
    editing.value = null
    await load()
  } catch (e) { error.value = e.message }
}
const toggle = async (r) => {
  error.value = ''
  try {
    await postJSON(`/api/interest-only-rules/${r.id}/${r.enabled ? 'disable' : 'enable'}`, {})
    await load()
  } catch (e) { error.value = e.message }
}
onMounted(load)
</script>
<template><div class="page"><h1>只息规则</h1>
<p>只息期数 K 须为正整数且小于贷款总期数；勾选只息后前 K 期只还利息，之后按等额本息重算。</p>
<p v-if="error" class="error">{{ error }}</p>
<h2>新建规则</h2>
<label>名称 <input v-model="newName" placeholder="只息12期" /></label>
<label>只息期数 K <input v-model.number="newK" type="number" min="1" /></label>
<button @click="create">创建</button>
<h2>规则列表</h2>
<table>
<tr><th>#</th><th>名称</th><th>只息期数 K</th><th>状态</th><th>操作</th></tr>
<tr v-for="r in items" :key="r.id">
  <td>{{ r.id }}</td>
  <td><template v-if="editing === r.id"><input v-model="editName" /></template><template v-else>{{ r.name }}</template></td>
  <td><template v-if="editing === r.id"><input v-model.number="editK" type="number" min="1" /></template><template v-else>{{ r.interest_only_months }}</template></td>
  <td>{{ r.enabled ? '启用' : '停用' }}</td>
  <td>
    <template v-if="editing === r.id">
      <button @click="saveEdit(r)">保存</button>
      <button @click="editing = null">取消</button>
    </template>
    <template v-else>
      <button @click="startEdit(r)">编辑</button>
      <button @click="toggle(r)">{{ r.enabled ? '停用' : '启用' }}</button>
    </template>
  </td>
</tr>
</table>
</div></template>
<style scoped>
h2 { font-size: 1rem; margin: 1rem 0 0.4rem; }
label { margin-right: 0.75rem; }
.error { color: #a33; }
button { margin-right: 0.3rem; }
</style>

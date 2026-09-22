<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const principal = ref(800000)
const annual_rate = ref(4.2)
const months = ref(360)
const interestOnly = ref(false)
const interestOnlyMonths = ref(12)
const rules = ref([])
const out = ref(null)
const error = ref('')
const run = async () => {
  error.value = ''
  const body = { principal: principal.value, annual_rate: annual_rate.value, months: months.value, persist: true }
  if (interestOnly.value) { body.interest_only = true; body.interest_only_months = interestOnlyMonths.value }
  try { out.value = await postJSON('/api/schedule', body) } catch (e) { error.value = e.message; out.value = null }
}
const pickRule = (e) => {
  const r = rules.value.find(x => x.id === Number(e.target.value))
  if (r) { interestOnlyMonths.value = r.interest_only_months; interestOnly.value = true }
}
onMounted(async () => { rules.value = (await getJSON('/api/interest-only-rules')).items.filter(r => r.enabled) })
</script>
<template><div class="page"><h1>等额本息试算</h1>
<label>本金 <input v-model.number="principal" /></label>
<label>年利率% <input v-model.number="annual_rate" /></label>
<label>月数 <input v-model.number="months" /></label>
<label>只息 <input type="checkbox" v-model="interestOnly" /></label>
<template v-if="interestOnly">
  <label>只息期数 K <input v-model.number="interestOnlyMonths" type="number" min="1" /></label>
  <label>按规则 <select @change="pickRule"><option value="">选择规则</option><option v-for="r in rules" :key="r.id" :value="r.id">{{ r.name }}（K={{ r.interest_only_months }}）</option></select></label>
</template>
<button @click="run">计算</button>
<p v-if="error" class="error">{{ error }}</p>
<template v-if="out && out.interest_only">
  <p>前 {{ out.interest_only_months }} 期月供（只息） <span class="hero-num">{{ out.monthly_payment_io }}</span> · 之后月供 <span class="hero-num">{{ out.monthly_payment_after }}</span></p>
  <p>利息合计 {{ out.total_interest }} · 还款总额 {{ out.total_payment }}</p>
  <table>
    <tr><th>期数</th><th>月供</th><th>本金</th><th>利息</th><th>剩余本金</th><th>分段</th></tr>
    <tr v-for="r in out.preview" :key="r.period">
      <td>{{ r.period }}</td><td>{{ r.payment }}</td><td>{{ r.principal }}</td><td>{{ r.interest }}</td><td>{{ r.balance }}</td>
      <td>{{ r.segment === 'interest_only' ? '只息' : '等额本息' }}</td>
    </tr>
  </table>
</template>
<p v-else-if="out">月供 {{ out.monthly_payment }} · 利息合计 {{ out.total_interest }}</p>
</div></template>
<style scoped>
label { margin-right: 0.75rem; }
.error { color: #a33; }
</style>

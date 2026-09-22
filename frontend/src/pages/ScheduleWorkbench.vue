<script setup>
import { computed, onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const principal = ref(800000)
const annual_rate = ref(4.2)
const months = ref(360)
const useIO = ref(false)
const rules = ref([])
const selectedRuleId = ref(null)
const customK = ref(12)
const out = ref(null)
const err = ref('')
const enabledRules = computed(() => rules.value.filter(r => r.enabled))
const kValue = computed(() => {
  const r = rules.value.find(x => x.id === selectedRuleId.value)
  return r ? r.interest_only_months : customK.value
})
const loadRules = async () => {
  rules.value = (await getJSON('/api/interest-only-rules')).items
  const first = enabledRules.value[0]
  if (first) selectedRuleId.value = first.id
}
const run = async (persist) => {
  err.value = ''
  const body = {
    principal: principal.value, annual_rate: annual_rate.value, months: months.value,
    persist, preview_rows: 24,
  }
  if (useIO.value) {
    body.interest_only = true
    body.interest_only_months = kValue.value
    const r = rules.value.find(x => x.id === selectedRuleId.value)
    if (r) body.interest_only_rule_id = r.id
  }
  try { out.value = await postJSON('/api/schedule', body) }
  catch (e) { err.value = String(e.message || e) }
}
const segOf = (period) => out.value?.segments
  ? (period <= out.value.interest_only_months ? out.value.segments[0] : out.value.segments[1])
  : null
onMounted(loadRules)
</script>
<template><div class="page"><h1>等额本息试算</h1>
<label>本金 <input v-model.number="principal" /></label>
<label>年利率% <input v-model.number="annual_rate" /></label>
<label>月数 <input v-model.number="months" /></label>
<div class="io-line">
  <label><input type="checkbox" v-model="useIO" /> 只息（先息后本）</label>
  <template v-if="useIO">
    <label>规则
      <select v-model="selectedRuleId">
        <option v-for="r in enabledRules" :key="r.id" :value="r.id">{{ r.name }}（K={{ r.interest_only_months }}）</option>
        <option :value="null">自定义 K</option>
      </select>
    </label>
    <label v-if="selectedRuleId === null">只息期数 K <input v-model.number="customK" type="number" min="1" /></label>
    <span v-else>只息期数 K = {{ kValue }}（需 &lt; 总期数 {{ months }}）</span>
  </template>
</div>
<button @click="run(true)">计算并存档</button>
<button @click="run(false)">仅试算</button>
<span v-if="err" class="err">{{ err }}</span>
<div v-if="out" class="result">
  <div v-if="out.interest_only" class="segments">
    <p>第 1–{{ out.interest_only_months }} 期（只息期）月供
      <span class="hero-num">{{ out.monthly_payment_interest_only }}</span></p>
    <p>第 {{ out.interest_only_months + 1 }}–{{ out.row_count }} 期（等额本息）月供
      <span class="hero-num">{{ out.monthly_payment_amortizing }}</span></p>
  </div>
  <p v-else>月供 <span class="hero-num">{{ out.monthly_payment }}</span></p>
  <p>利息合计 {{ out.total_interest }} · 总还款 {{ out.total_payment }}
    <span v-if="out.run_id" class="tag">已存档 #{{ out.run_id }}</span>
    <span v-else class="tag muted">未写记录</span>
  </p>
  <table>
    <tr><th>期次</th><th>分段</th><th>月供</th><th>本金</th><th>利息</th><th>余额</th></tr>
    <tr v-for="r in out.preview" :key="r.period">
      <td>{{ r.period }}</td>
      <td>{{ r.segment === 'interest_only' ? '只息' : (r.segment === 'amortizing' ? '本息' : '—') }}</td>
      <td>{{ r.payment }}</td><td>{{ r.principal }}</td><td>{{ r.interest }}</td><td>{{ r.balance }}</td>
    </tr>
  </table>
</div>
</div></template>
<style scoped>
label { margin-right:0.75rem; }
.io-line { margin:0.5rem 0; display:flex; gap:0.75rem; align-items:center; flex-wrap:wrap; }
.segments p { margin:0.25rem 0; }
.tag { margin-left:0.5rem; background:#eee; padding:0 0.4rem; }
.tag.muted { color:#888; }
.err { color:#a33; }
</style>

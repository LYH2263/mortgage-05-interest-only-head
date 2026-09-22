<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON } from '../api'
const route = useRoute()
const run = ref(null)
const err = ref('')
const load = async () => {
  err.value = ''
  try { run.value = await getJSON(`/api/history/${route.params.id}`) }
  catch (e) { err.value = String(e.message || e) }
}
onMounted(load); watch(() => route.params.id, load)
</script>
<template><div class="page" v-if="run"><h1>旧条 #{{ run.id }}</h1>
<p class="note">以下为写入时的落库快照，规则页后续修改 K 不影响本条口径。</p>
<h2>入参</h2>
<table>
  <tr><td>本金</td><td>{{ run.input.principal }}</td></tr>
  <tr><td>年利率%</td><td>{{ run.input.annual_rate }}</td></tr>
  <tr><td>总期数</td><td>{{ run.input.months }}</td></tr>
  <tr><td>只息</td><td>{{ run.input.interest_only ? '是' : '否' }}</td></tr>
  <tr v-if="run.input.interest_only"><td>只息期数 K（落库）</td><td>{{ run.input.interest_only_months }}</td></tr>
  <tr v-if="run.input.interest_only"><td>规则 ID</td><td>{{ run.input.interest_only_rule_id ?? '自定义' }}</td></tr>
</table>
<h2>结果</h2>
<div v-if="run.result.interest_only" class="segments">
  <p>第 1–{{ run.result.interest_only_months }} 期（只息期）月供
    <span class="hero-num">{{ run.result.monthly_payment_interest_only }}</span></p>
  <p>第 {{ run.result.interest_only_months + 1 }}–{{ run.result.row_count }} 期（等额本息）月供
    <span class="hero-num">{{ run.result.monthly_payment_amortizing }}</span></p>
</div>
<p v-else>月供 <span class="hero-num">{{ run.result.monthly_payment }}</span></p>
<p>利息合计 {{ run.result.total_interest }} · 总还款 {{ run.result.total_payment }}</p>
<table v-if="run.result.preview">
  <tr><th>期次</th><th>分段</th><th>月供</th><th>本金</th><th>利息</th><th>余额</th></tr>
  <tr v-for="r in run.result.preview" :key="r.period">
    <td>{{ r.period }}</td>
    <td>{{ r.segment === 'interest_only' ? '只息' : (r.segment === 'amortizing' ? '本息' : '—') }}</td>
    <td>{{ r.payment }}</td><td>{{ r.principal }}</td><td>{{ r.interest }}</td><td>{{ r.balance }}</td>
  </tr>
</table>
<p v-if="err" class="err">{{ err }}</p>
</div></template>
<style scoped>
.note { color:#665; }
.segments p { margin:0.25rem 0; }
.err { color:#a33; }
</style>

<template>
  <el-dialog v-model="visible" title="任务结果" width="60%">
    <div v-if="result">
      <h4>建议</h4>
      <div class="markdown-content" v-html="renderMarkdown(getRecommendation() || '无')"></div>
      <h4 style="margin-top: 16px;">摘要</h4>
      <div class="markdown-content" v-html="renderMarkdown(getSummary() || '无')"></div>
    </div>
    <template #footer>
      <el-button @click="emit('close')">关闭</el-button>
      <el-button type="primary" @click="emit('view-report')">查看报告详情</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps<{ modelValue: boolean; result: any }>()
const emit = defineEmits(['update:modelValue','close','view-report'])

const visible = computed({
  get: () => props.modelValue,
  set: (v: boolean) => emit('update:modelValue', v)
})

marked.setOptions({ breaks: true, gfm: true })
const renderMarkdown = (s: string) => { try { return marked.parse(s||'') as string } catch { return s } }

// 获取建议：优先使用 result.recommendation，如果没有则尝试从 result_data.recommendation 获取
const getRecommendation = () => {
  if (!props.result) return ''
  // 优先使用顶层 recommendation
  if (props.result.recommendation) return props.result.recommendation
  // 尝试从 result_data 中获取
  if (props.result.result_data?.recommendation) return props.result.result_data.recommendation
  return ''
}

// 获取摘要：优先使用 result.summary，如果没有则尝试从 result_data.decision.reasoning 获取
const getSummary = () => {
  if (!props.result) return ''
  // 优先使用顶层 summary
  if (props.result.summary) return props.result.summary
  // 尝试从 result_data.decision.reasoning 获取
  // if (props.result.decision?.reasoning) return props.result.decision.reasoning
  // 尝试从 result_data.summary 获取
  // if (props.result.result_data?.summary) return props.result.result_data.summary
  return ''
}
</script>


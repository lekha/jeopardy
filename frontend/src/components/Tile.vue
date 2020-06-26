<template>
<div class="tile">
  <p class="points">${{ points }}<p>
</div>
</template>

<script>
export default {
  name: "Tile",
  props: {
    points: Number,
    answer: String,
    question: String
  },
  data() {
    return {
      points: 0,
      answer: "Blank answer",
      question: "Blank question"
    }
  }
}
</script>

<template>
<div class="tile">
  <p class="points">${{ points }}</p>
</div>
</template>

<script>
export default {
  name: "Tile",
  data() {
    return {
      points: this.tile.points,
      answer: this.tile.answer,
      question: this.tile.question
    }
  },
  props: {
    tile: Object
  }
}
</script>

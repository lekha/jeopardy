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
    }
  },
  computed: {
    points() { return this.tile.points; },
    answer() { return this.tile.answer; },
    question() { return this.tile.question; }
  },
  props: {
    tile: Object
  }
}
</script>

<template>
<div class="game">
  <p>Code: {{ code }}</p>
  <p>Round: {{ round_class }}</p>
  <board v-bind:board="board"></board>
</div>
</template>

<script>
import Board from "./board.vue";

export default {
  name: "Game",
  components: {
    "board": Board
  },
  data() {
    return {
      code: this.game.code,
      round_class: this.game.round_.class_,
      board: this.game.round_.board
    }
  },
  props: {
    game: Object
  }
}
</script>

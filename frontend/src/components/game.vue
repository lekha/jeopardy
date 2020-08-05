<template>
<div class="game">
  <p>Code: {{ code }}</p>
  <p>Round: {{ round_class }}</p>
  <board v-bind:board="board"></board>
  <ul>
    <li v-for="team in teams" v-bind:key="team.id">
      <team v-bind:team="team"></team>
    </li>
  </ul>
</div>
</template>

<script>
import Board from "./board.vue";
import Team from "./team.vue";

export default {
  name: "Game",
  components: {
    "board": Board,
    "team": Team
  },
  data() {
    return {
    }
  },
  computed: {
    code() { return this.game.code; },
    round_class() { return this.game.round_.class_; },
    board() { return this.game.round_.board; },
    teams() { return this.game.teams; }
  },
  props: {
    game: Object
  }
}
</script>

<template>
<div class="game">
  <p>Code: {{ code }}</p>

    <template v-if="display.level=='game'">
      <p>Round: {{ round_class }}</p>
      <ul>
        <li v-for="team in teams" v-bind:key="team.id">
          <team
            v-bind:team="team" v-bind:socket="socket"></team>
        </li>
      </ul>
      <board v-bind:board="board"></board>
    </template>

    <template v-else-if="display.level='team'">
      <ul>
        <li v-for="team in teams" v-bind:key="team.id">
          <team
            v-bind:team="team"
            v-bind:is_joinable="game.status=='joinable'"
            v-bind:socket="socket">
          </team>
        </li>
      </ul>
    </template>

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
    display() { return this.game.display; },
    round_class() { return this.game.round_.class_; },
    board() { return this.game.round_.board; },
    teams() { return this.game.teams; }
  },
  props: {
    game: Object,
    socket: WebSocket
  }
}
</script>

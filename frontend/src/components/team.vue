<template>
<div class="team">
  <p>Team: {{ name }}</p>
  <ul>
    <li v-for="player in players" v-bind:key="player.id">
      <player v-bind:player="player"></player>
    </li>
  </ul>
</div>
</template>

<script>
import Player from "./player.vue";

export default {
  name: "Team",
  components: {
    "player": Player
  },
  data() {
    return {
    }
  },
  computed: {
    name() { return this.team.name; },
    has_pressed_buzzer() { return this.team.has_pressed_buzzer; },
    players() { return this.team.players; }
  },
  props: {
    team: Object
  }
}
</script>

<template>
<base-layout>
  <template v-slot:main>
    <template v-if="game">
      <game v-bind:game="game"></game>
    </template>
    <p v-else>Game not found for code: {{ gameCode }}</p>
  </template>
</base-layout>
</template>

<script>
import { api } from "@/api";
import BaseLayout from "@/layouts/base.vue";
import Game from "@/components/game.vue";

export default {
  name: "Host",
  components: {
    "base-layout": BaseLayout,
    "game": Game
  },
  data() {
    return {
      game: null,
      gameCode: this.$route.params.gameCode
    }
  },
  methods: {
    setGame() {
      api.getGame(this.gameCode)
      .then(game => {
        this.game = game;
      });
    }
  },
  beforeMount() {
    this.game = this.setGame();
  }
}
</script>

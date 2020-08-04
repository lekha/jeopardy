<template>
<base-layout>
  <template v-slot:main>
    <button v-on:click="createGame">Create</button>
    <template v-if="game">
      <game v-bind:game="game"></game>
    </template>
  </template>
</base-layout>
</template>

<script>
import { api } from "@/api";
import BaseLayout from "@/layouts/base.vue";
import Game from "@/components/game.vue";

export default {
  name: "Create",
  components: {
    "base-layout": BaseLayout,
    "game": Game
  },
  data() {
    return {
      game: null
    }
  },
  methods: {
    createGame() {
      api.createGame()
      .then(game => {
        this.game = game;
      });
    }
  }
}
</script>

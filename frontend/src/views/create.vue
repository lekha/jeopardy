<template>
<base-layout>
  <template v-slot:main>
    <button v-on:click="createGame">Create</button>
    <template v-if="board">
      <p>Code: {{ board.code }}</p>
    </template>
  </template>
</base-layout>
</template>

<script>
import BaseLayout from "../layouts/base.vue";

export default {
  name: "Create",
  components: {
    "base-layout": BaseLayout
  },
  data() {
    return {
      board: null
    }
  },
  methods: {
    createGame() {
      this.$http.post("api/v1/game")
      .then(response => {
        this.board = response.data;
      })
    }
  }
}
</script>

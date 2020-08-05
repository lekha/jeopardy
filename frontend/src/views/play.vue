<template>
<base-layout>
  <template v-slot:main>
    <div class="play">
      <template v-if="game">
        <game v-bind:game="game" v-bind:socket="socket"></game>
      </template>
      <p v-else>Game not found for code: {{ gameCode }}</p>
    </div>
  </template>
</base-layout>
</template>

<script>
import BaseLayout from "@/layouts/base.vue";
import Game from "@/components/game.vue";

export default {
  name: "Play",
  components: {
    "base-layout": BaseLayout,
    "game": Game
  },
  data() {
    return {
      game: null,
      gameCode: this.$route.params.gameCode,
      socket: null
    }
  },
  computed: {
    display() { return this.game.display; }
  },
  methods: {
    backendConnection(gameCode) {
      var path = "ws://127.0.0.1/api/v1/play/" + gameCode;
      var socket = new WebSocket(path);

      socket.onopen = function(event) {
        console.log(event);
      }

      socket.onmessage = (event) => {
        console.log(event);
        var response = JSON.parse(event.data);
        const { status_code: statusCode } = response;
        if (statusCode == 302) {
            const { redirect_url : redirectUrl } = response;
            this.redirectTo(redirectUrl);
        }
        console.log(response);
        this.game = JSON.parse(response);
      }

      return socket;
    },
    redirectTo(url) {
      location.href = url;
    }
  },
  mounted() {
    this.socket = this.backendConnection(this.$route.params.gameCode);
  }
}
</script>

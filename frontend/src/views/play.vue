<template>
<div class="play">
  <p>This is the game play page.</p>
</div>
</template>

<script>
export default {
  name: "Play",
  data() {
    return {
      socket: ""
    }
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
      }

      return socket;
    },
    redirectTo(url) {
      location.href = url;
    }
  },
  beforeMount() {
    this.socket = this.backendConnection(this.$route.params.gameCode);
  }
}
</script>

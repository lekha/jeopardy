<template>
<p class="player">{{ username }}</p>
</template>

<script>
export default {
  name: "Player",
  data() {
    return {
      username: this.player.username,
    }
  },
  props: {
    player: Object
  }
}
</script>
